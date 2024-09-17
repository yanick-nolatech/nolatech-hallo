import os
import glob
import subprocess
import argparse
from datetime import datetime
import time
import pandas as pd

WORKDIR = os.path.dirname(__file__)
DATADIR = os.path.join(WORKDIR, 'data')

# IMAGE_DIMS = [512]

sources_dir = os.path.join(DATADIR, 'sources')
driving_dir = os.path.join(DATADIR, 'driving')
animations_dir = os.path.join(DATADIR, 'animations')
exec_time_dir = os.path.join(DATADIR, 'exec_time')

sources_files = glob.glob(os.path.join(sources_dir, '*.*'))
sources_files
driving_files = glob.glob(os.path.join(driving_dir, '*.wav'))
driving_files




def create_animnation(
        source_file: str,
        driving_file: str,
        output_path: str,
        # image_dim: int
        ):
    
    assert os.path.exists(source_file)
    assert os.path.exists(driving_file)
    CMD = [
        'python',
        'scripts/inference.py',
        '--source_image',
        source_file,
        '--driving_audio',
        driving_file,
        '--output',
        output_path,
    ]
    print(CMD)
    subprocess.run(CMD, check=True)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('system_name')
    args = parser.parse_args()
    system_name: str = args.system_name

    exec_time_db = []

    for source_file in sources_files:
        print('source', source_file)
        source_name = os.path.splitext(os.path.basename(source_file))[0]
        output_dir = os.path.join(animations_dir, source_name)
        os.makedirs(output_dir, exist_ok=True)
        for driving_file in driving_files:
            print('driving', driving_file)
            driving_name = os.path.splitext(os.path.basename(driving_file))[0]

            # for image_dim in IMAGE_DIMS:
                # print(image_dim)
            output_path = os.path.join(output_dir, f'{source_name}_{driving_name}.mp4')
            if not os.path.exists(output_path):
                start_time = time.time()
                create_animnation(source_file, driving_file, output_path)
                elapsed_time = time.time() - start_time
                exec_time_db.append((source_name, driving_name, elapsed_time))


    if exec_time_db:
        current_date = datetime.now().isoformat()
        exec_time_path = os.path.join(exec_time_dir, f'{system_name}_{current_date}.csv')
        pd_exec_time = pd.DataFrame(exec_time_db, columns=['source', 'driving', 'time'])
        pd_exec_time['system_name'] = system_name

        os.makedirs(exec_time_dir, exist_ok=True)
        pd_exec_time.to_csv(exec_time_path, index=False)





