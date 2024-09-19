import os
import subprocess
from omegaconf import OmegaConf
import copy
import tempfile
import pprint
import time
import json
from typing import List, Dict, Any, Iterator
import itertools

WORKDIR = os.path.dirname(__file__)
DATADIR = os.path.join(WORKDIR, 'data')

sources_dir = os.path.join(DATADIR, 'sources')
driving_dir = os.path.join(DATADIR, 'driving')
animations_dir = os.path.join(DATADIR, 'animations')
exec_time_dir = os.path.join(DATADIR, 'exec_time')

def get_filename(file: str) -> str:
    return os.path.splitext(os.path.basename(file))[0]

def write_json(config: Dict[str, Any], path: str):
    with open(path, 'w') as f:
        json.dump(config, f)


def create_animnation(
        config_file: str,
        output_path: str,
        ):
    
    assert os.path.exists(config_file)
    CMD = [
        'python',
        'scripts/inference.py',
        '--config',
        config_file,
        '--output',
        output_path,
    ]
    print(CMD)
    subprocess.run(CMD, check=True)



IMAGE_RES = [256, 512]
SAMPLING_STEPS = [20, 30, 40]

PARAMETER_GRID = {
    'image_res': IMAGE_RES,
    'inference_steps': SAMPLING_STEPS
}


def get_combinations(parameter_grid: Dict[str, List[Any]]) -> Iterator[Dict[str, Any]]:
    param_names = list(parameter_grid.keys())
    for combination in itertools.product(*parameter_grid.values()):
        yield {k: v for k, v in zip(param_names, combination)}


if __name__ == '__main__':
    driving_file = os.path.join(driving_dir, 'spanish_test.wav')
    source_file = os.path.join(sources_dir, 'SquareMaduroMic1768.jpg')
    source_config_file = "configs/inference/default.yaml"

    grid = get_combinations(PARAMETER_GRID)
    source_config = OmegaConf.load(source_config_file)
    source_config['source_image'] = source_file
    source_config['driving_audio'] = driving_file

    source_name = get_filename(source_file)
    driving_name = get_filename(driving_file)
    source_and_driving_name = f'{source_name}_{driving_name}'
    output_dir = os.path.join(animations_dir, 'configurations', source_and_driving_name)
    os.makedirs(output_dir, exist_ok=True)

    for parameters in grid:
        config = copy.deepcopy(source_config)
        config['data']['source_image']['width'] = parameters['image_res']
        config['data']['source_image']['height'] = parameters['image_res']
        config['inference_steps'] = parameters['inference_steps']

        parameters_name = '_'.join(f'{k}={v}' for k, v in parameters.items())
        output_name = f'{parameters_name}.mp4'
        output_path = os.path.join(output_dir, output_name)
        pprint.pprint(config)

        metadata_path = os.path.join(output_dir, f'{parameters_name}_metadata.json')

        if os.path.exists(output_path):
            continue

        with tempfile.NamedTemporaryFile(suffix='.yml') as tmpfile:
            OmegaConf.save(config, tmpfile.name)
            assert os.path.exists(tmpfile.name)
            start_time = time.time()
            create_animnation(tmpfile.name, output_path)
            exec_time = time.time() - start_time
            print(f'exec_time: {exec_time}')


        metadata = {**parameters}
        metadata['source'] = source_name
        metadata['driving'] = driving_name
        metadata['exec_time'] = exec_time
        metadata['path'] = output_path
        write_json(metadata, metadata_path)

