from constants import ROOT_DIR



LOG_DIR = f'{ROOT_DIR}/data/logs'



def log(message: str, file: str) -> None:
    '''
    Log urls in case they need to be looked at later.
    '''

    with open(f'{LOG_DIR}/{file}', 'a') as f:
        f.write(message)

