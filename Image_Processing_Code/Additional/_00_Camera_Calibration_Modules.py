import configparser
import numpy as np

def save_camera_config(filename, camera_matrix, dist_coeffs=None):
    config = configparser.ConfigParser()
    
    # Convert matrix to string (comma-separated for readability)
    # We use flatten to make it a single line or keep it as is
    matrix_str = ','.join(map(str, camera_matrix.flatten()))
    
    config['CAMERA_PARAMS'] = {
        'intrinsic_matrix': matrix_str,
        'rows': str(camera_matrix.shape[0]),
        'cols': str(camera_matrix.shape[1])
    }
    
    if dist_coeffs is not None:
        config['CAMERA_PARAMS']['distortion_coefficients'] = ','.join(map(str, dist_coeffs.flatten()))

    with open(filename, 'w') as configfile:
        config.write(configfile)
    print(f"Configuration saved to {filename}")



def load_camera_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    
    # Retrieve string and convert back to numpy array
    matrix_str = config.get('CAMERA_PARAMS', 'intrinsic_matrix')
    rows = config.getint('CAMERA_PARAMS', 'rows')
    cols = config.getint('CAMERA_PARAMS', 'cols')
    dist_Coeff = config.get('CAMERA_PARAMS', 'distortion_coefficients')
    
    matrix = np.fromstring(matrix_str, sep=',').reshape(rows, cols)
    if dist_Coeff is not None:
        dist_Coeff = np.fromstring(dist_Coeff, sep=',')
    return matrix, dist_Coeff