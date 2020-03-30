from data_analysis.util.folder_init import init_folder_md_json_file
from data_analysis.util.get_configurations import get_config_dict_via_hostname
from data_analysis.util.read_file_utils_updated import *
from data_analysis.util.parsing_helpers import *
from data_analysis.aec_algorithm.local_config.ktruss_exec_tags import *
from data_analysis.aec_algorithm.local_config.load_data import *

from config import *
from exec_utilities import exec_utils
import json

user_output_md_file = '2020-01-10-CPU-PP-SI.md'
config_lst = ['exp-2020-01-09', [
    'pkt-eid',
    'pkt-eid-parallel',
    'pkt-eval-tc-baseline',
    'pkt-eval-tc-dtc',
    'pkt-eval-tc-wp',
    'cuda-pkt-offload'], ['gpu24']]

PP_SI_tag_lst = ['TC Time', 'End-To-End Time', 'Init Eid Time']


def fetch_statistics(root_dir, dataset_lst, reorder_tag, t_lst, algorithm, json_file_path):
    # Dataset -> Thread Num -> Detailed Time Info
    my_dict = dict()
    for dataset in dataset_lst:
        my_dict[dataset] = dict()
        for t_num in t_lst:
            file_path = os.sep.join([root_dir, dataset, reorder_tag, t_num, algorithm + '.log'])
            logger.info(file_path)
            lines = get_file_lines(file_path)

            my_dict[dataset][t_num] = parse_lines_cuda(lines, PP_SI_tag_lst)
    with open(json_file_path, 'w') as ofs:
        ofs.write(json.dumps(my_dict, indent=4))


def generate_md(dataset_lst, json_file_path, logger, output_md_file):
    data_names = get_data_set_names('local_config')

    with open(json_file_path) as ifs:
        data_dict = json.load(ifs)

        # t_num = str(max(map(int, t_lst)))
        t_num = str(64)
        lines = [['Dataset'] + PP_SI_tag_lst, ['---' for _ in range(len(PP_SI_tag_lst) + 1)]]

        # Dataset -> Thread Num -> Detailed Time Info
        for data_set in dataset_lst:
            time_lst = [data_dict[data_set][t_num][k] for k in PP_SI_tag_lst]
            if len(list(filter(lambda e: e is None, time_lst))) == 1 and time_lst[-1] is None:
                time_lst[-1] = sum(time_lst[:-1])
            lines.append([data_names[data_set]] + time_lst)

    bold_line = '-'.join([my_md_algorithm_name, '(' + get_comment(my_md_algorithm_name) + ')'])
    generate_md_table_from_lines(bold_line, lines, logger, output_md_file)


if __name__ == '__main__':
    base_dir = '/home/yche/'
    # base_dir = '/Users/cheyulin/'
    os.system('mkdir -p {}logs/'.format(base_dir))
    my_res_log_file_folder = config_lst[0]
    my_gpu_lst = config_lst[2]

    for hostname in my_gpu_lst:
        app_md_path = init_folder_md_json_file('..', hostname, user_output_md_file)
        for my_md_algorithm_name in config_lst[1]:
            json_file_path = my_res_log_file_folder + '-' + my_md_algorithm_name + '.json'
            json_file_path = os.sep.join(['../data-json/', hostname, json_file_path])
            log_path = my_res_log_file_folder + '-' + my_md_algorithm_name + '.log'
            logger = exec_utils.get_logger('{}logs/'.format(base_dir) + log_path, __name__)

            with open(app_md_path, 'a+') as output_md_file:
                # Dataset -> Thread Num -> Detailed Time Info
                config_dict = get_config_dict_via_hostname(hostname)
                root_dir = '{}mnt/luocpu9/mnt/storage1/yche/git-repos/' \
                           'OutOfCoreSCAN/python_experiments/exp_results/{}/{}'. \
                    format(base_dir, 'exp-2020-01-09', 'gpu24')
                dataset_lst = load_data_sets()
                reorder_tag = 'org'
                t_lst = list(map(str, config_dict[thread_num_lst_tag]))
                # Fetch data and parse it as a markdown file
                fetch_statistics(root_dir=root_dir, dataset_lst=dataset_lst, reorder_tag=reorder_tag, t_lst=t_lst,
                                 algorithm=my_md_algorithm_name, json_file_path=json_file_path)
                generate_md(dataset_lst, json_file_path, logger, output_md_file)