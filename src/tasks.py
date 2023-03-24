from celery.utils.log import get_task_logger
import tempfile
import os
import time

from pareto_algorithms_and_metrics.main import run_optimization
from support_modules.constraints_generator import generate_constraint_file

from factory import create_celery, create_app

logger = get_task_logger(__name__)
celery = create_celery(create_app())


@celery.task(name='optimization_task')
def optimization_task(model_filename, sim_params_file, cons_params_file, num_instances, algorithm, approach, log_name):
    logger.info(f'Model file: {model_filename}')
    logger.info(f'Sim params file: {sim_params_file}')
    logger.info(f'Cons params file: {cons_params_file}')
    logger.info(f'Num of instances: {num_instances}')
    logger.info(f'Algorithm: {algorithm}')
    logger.info(f'Approach: {approach}')

    curr_dir_path = os.path.abspath(os.path.dirname(__file__))
    celery_data_path = os.path.abspath(os.path.join(curr_dir_path, 'celery/data'))

    model_path = os.path.abspath(os.path.join(celery_data_path, model_filename))
    sim_param_path = os.path.abspath(os.path.join(celery_data_path, sim_params_file))
    constraints_path = os.path.abspath(os.path.join(celery_data_path, cons_params_file))

    # create result file for saving report
    stats_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".json", prefix="stats_", delete=False,
                                             dir=celery_data_path)
    stats_filename = stats_file.name.rsplit(os.sep, 1)[-1]

    # # create result file for saving logs
    # logs_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", prefix="logs_", delete=False,
    #                                         dir=celery_data_path)
    # logs_filename = logs_file.name.rsplit(os.sep, 1)[-1]

    report = run_optimization(model_path, sim_param_path, constraints_path, num_instances, algorithm, approach,
                              stats_file.name, log_name)

    return {
        "stat_path": stats_filename,
        "report": report
    }

@celery.task(name='cons_generation_task')
def generate_constraints(sim_params_file, out_file=''):
    logger.info(f'Sim params file: {sim_params_file}')
    logger.info(f'Out file: {out_file}')

    curr_dir_path = os.path.abspath(os.path.dirname(__file__))
    celery_data_path = os.path.abspath(os.path.join(curr_dir_path, 'celery/data'))

    sim_param_path = os.path.abspath(os.path.join(celery_data_path, sim_params_file))

    generated_constraints = generate_constraint_file(sim_param_path, out_file)

    return {
        "constraints": generated_constraints
    }




@celery.task()
def clear_celery_folder():
    curr_dir_path = os.path.abspath(os.path.dirname(__file__))
    celery_data_path = os.path.abspath(os.path.join(curr_dir_path, 'celery/data'))

    now = time.time()
    deleted_files_count = 0

    for f in os.listdir(celery_data_path):
        if f == "README.md":
            continue

        file_path = os.path.join(celery_data_path, f)
        if os.path.isfile(file_path):
            if os.stat(file_path).st_mtime < now - 1 * 3600:
                # if the age of the file is bigger than 1 hour
                logger.info(f'{f} file removing ...')
                os.remove(file_path)
                deleted_files_count = deleted_files_count + 1

    logger.info(f'In total deleted: {deleted_files_count} file(s) ')
