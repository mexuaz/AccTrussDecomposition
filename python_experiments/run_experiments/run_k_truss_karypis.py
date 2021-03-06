import socket

from exec_utilities import time_out_util
from config import *
from exec_utilities.exec_utils import *
from multiprocessing import Process


def run_exp(env_tag=knl_tag, with_c_group=True, data_path_tag=karypis_k_truss_exec_path_tag):
    hostname = socket.gethostname()

    with open('config.json') as ifs:
        my_config_dict = json.load(ifs)[env_tag]
    our_exec_path = my_config_dict[data_path_tag]
    data_set_path = my_config_dict[data_set_path_tag]
    # thread_num_lst = my_config_dict[thread_num_lst_tag]
    thread_num_lst = [40]
    data_set_lst = my_config_dict[data_set_lst_tag]
    exp_res_root_name = 'exp_results'
    folder_name = 'exp-2019-10-07-msp' + os.sep + hostname

    our_exec_name_lst = [
        # 'ktruss-improved',    # for AND only
        'ktruss']
    kt_type_dict = {
        'ustgpu2': 'msp',
        'ustgpu1': 'msp'
    }
    kt_type_name = kt_type_dict[hostname.strip()]

    work_dir = os.sep.join(['.', exp_res_root_name, folder_name])
    os.system('mkdir -p ' + work_dir)
    logger = get_logger(os.sep.join([work_dir, hostname + '.log']), name=__name__)

    logger.info(my_splitter + time.ctime() + my_splitter)
    logger.info('res folder: {}'.format(folder_name))
    logger.info('our exec folder: {}'.format(our_exec_path))
    logger.info('our exec name list: {}'.format(our_exec_name_lst))
    logger.info('thread# lst: {}'.format(thread_num_lst))
    logger.info('data set lst: {}'.format(data_set_lst))

    def one_round():
        for data_set_name in data_set_lst:
            # force quitting the OOM computation
            if data_set_name == 'webgraph_eu' and kt_type_name == 'msp':
                continue
            for our_algorithm in our_exec_name_lst:

                for t_num in thread_num_lst:
                    statistics_dir = os.sep.join(map(str, ['.', exp_res_root_name, folder_name, data_set_name, t_num]))
                    os.system('mkdir -p ' + os.sep.join([statistics_dir, 'log']))
                    statistics_file_path = statistics_dir + os.sep + our_algorithm + '-' + kt_type_name + '.log'
                    dstat_file_path = statistics_dir + os.sep + our_algorithm + '-' + kt_type_name + '-dstat.log'
                    log_file_path = os.sep.join(
                        [statistics_dir, 'log', '-'.join([our_algorithm, kt_type_name, 'raw.log'])])
                    logger.info('stat file path: {}'.format(statistics_file_path))
                    logger.info('log file path: {}'.format(log_file_path))

                    # 1st: append headers
                    append_header(statistics_file_path)
                    append_header(dstat_file_path)
                    append_header(log_file_path)

                    # 2nd: run exec cmd
                    algorithm_path = our_exec_path + os.sep + our_algorithm
                    params_lst = map(str, ['cgexec -g memory:yche-exp' if with_c_group else '', algorithm_path,
                                           '-kttype', kt_type_name, '-iftype', 'bin', '-logfile', statistics_file_path,
                                           data_set_path + os.sep + data_set_name])
                    cmd = ' '.join(params_lst)
                    logger.info('exec-cmd: {}'.format(cmd))
                    time_out = 3600 * 5
                    my_env = os.environ.copy()

                    def execute_cmd(my_cmd):
                        logger.info('sub-process: {}'.format(my_cmd))
                        os.system(my_cmd)

                    # 3rd: spawn a new process to run the exec
                    dstat_cmd = 'dstat -tcdrlmgyn --fs >> ' + dstat_file_path
                    p = Process(target=execute_cmd, args=(dstat_cmd,))
                    p.start()
                    my_env['OMP_NUM_THREADS'] = str(t_num)
                    tle_flag, info, correct_info = time_out_util.run_with_timeout(cmd, timeout_sec=time_out,
                                                                                  env=my_env)
                    time_out_util.kill_term_recursive(p.pid)
                    modify_dstat_file(dstat_file_path)

                    # 4th: append outputs
                    write_split(statistics_file_path)
                    with open(statistics_file_path, 'a+') as ifs:
                        ifs.write(correct_info)
                        ifs.write('\nis_time_out:' + str(tle_flag))
                        ifs.write(my_splitter + time.ctime() + my_splitter)
                        ifs.write('\n\n\n\n')
                    if len(info) > 0:
                        with open(log_file_path, 'a+') as ofs:
                            ofs.write(info)

                    logger.info('finish: {}'.format(cmd))

    one_round()


if __name__ == '__main__':
    hostname = socket.gethostname()
    if hostname.startswith('ustgpu2'):
        run_exp(env_tag=ustgpu2_tag, with_c_group=False)
    elif hostname.startswith('ustgpu1'):
        run_exp(env_tag=ustgpu1_tag, with_c_group=False)
    elif hostname.startswith('lccpu12'):
        run_exp(lccpu12_tag, False)
    elif hostname.startswith('gpu23'):
        run_exp(env_tag=gpu23_tag)
    elif hostname.startswith('gpu'):
        run_exp(env_tag=gpu_other_tag)
    else:
        # run_exp(env_tag=knl_tag, data_path_tag=exec_path_tag)
        run_exp(env_tag=knl_tag, data_path_tag=exec_path_non_hbw_tag)
