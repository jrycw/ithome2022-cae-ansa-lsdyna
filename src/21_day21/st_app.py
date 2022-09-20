import json
from datetime import datetime
from io import BytesIO

import boto3
import streamlit as st
from pydantic import BaseModel

st.set_page_config('Box Drop',  layout='centered')
st.header('Box Drop Config')


class PlateModel(BaseModel):
    l_p: float
    w_p: float
    en1_p: int
    en2_p: int
    z_elv_p: float
    move_x_p: float
    move_y_p: float
    rot_angle_p: float


class BoxModel(BaseModel):
    l_b: float
    w_b: float
    h_b: float
    en1_b: int
    en2_b: int
    en3_b: int
    z_elv_b: float
    move_x_b: float
    move_y_b: float
    rot_angle_b: float


class CRTLParamsModel(BaseModel):
    vz: float
    endtim: float


class S3Credentials(BaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str
    endpoint_url: str


class MyS3:
    def __init__(self, s3_credentials):
        self.s3_credentials = s3_credentials

    def get_s3_client(self):
        if hasattr(self, 's3_client'):
            return self.s3_client
        self.s3_client = boto3.client('s3', **self.s3_credentials)
        return self.s3_client


def get_my_s3():
    s3_credentials = S3Credentials(aws_access_key_id=st.secrets['aws_access_key_id'],
                                   aws_secret_access_key=st.secrets['aws_secret_access_key'],
                                   endpoint_url=st.secrets['endpoint_url'])
    return MyS3(s3_credentials=s3_credentials.dict())


def main():
    with st.form('submit-form'):
        plate = st.container()
        box = st.container()
        crtl_params = st.container()

        with plate:
            st.write('Plate')

            col_11, col_12 = st.columns(2)
            with col_11:
                l_p = st.number_input('l_p(mm)', value=100.0, step=1.0)
            with col_12:
                w_p = st.number_input('w_p(mm)', value=100.0, step=1.0)

            col_21, col_22 = st.columns(2)
            with col_21:
                en1_p = st.number_input('en1_p', value=10, min_value=1)
            with col_22:
                en2_p = st.number_input('en2_p', value=10, min_value=1)

            col_31, col_32, col_33, col_34 = st.columns(4)
            with col_31:
                z_elv_p = st.number_input('z_elv_p', value=0.0, step=1.0)
            with col_32:
                move_x_p = st.number_input('move_x_p(mm)', value=0.0, step=1.0)
            with col_33:
                move_y_p = st.number_input('move_y_p(mm)', value=0.0, step=1.0)
            with col_34:
                rot_angle_p = st.number_input(
                    'rot_angle_p(deg)', value=0.0, min_value=0.0, max_value=360.0, step=1.0)

        with box:
            st.write('Box')

            col_51, col_52, col_53 = st.columns(3)
            with col_51:
                l_b = st.number_input('l_b(mm)', value=50.0, step=1.0)
            with col_52:
                w_b = st.number_input('w_b(mm)', value=50.0, step=1.0)
            with col_53:
                h_b = st.number_input('h_b(mm)', value=50.0, step=1.0)

            col_61, col_62, col_63 = st.columns(3)
            with col_61:
                en1_b = st.number_input('en1_b', value=10, min_value=1)
            with col_62:
                en2_b = st.number_input('en2_b', value=10, min_value=1)
            with col_63:
                en3_b = st.number_input('en3_b', value=10, min_value=1)

            col_71, col_72, col_73, col_74 = st.columns(4)
            with col_71:
                z_elv_b = st.number_input('z_elv_b(mm)', value=5.0, step=1.0)
            with col_72:
                move_x_b = st.number_input(
                    'move_x_b(mm)', value=50.0, step=1.0)
            with col_73:
                move_y_b = st.number_input(
                    'move_y_b(mm)', value=20.0, step=1.0)
            with col_74:
                rot_angle_b = st.number_input(
                    'rot_angle_b(deg)', value=45.0, min_value=0.0, max_value=360.0, step=1.0)

        with crtl_params:
            st.write('Control params')

            col_101, col_102 = st.columns(2)
            with col_101:
                vz = st.number_input('vz(mm/s)', value=-500.0, step=1.0)
            with col_102:
                endtim = st.number_input(
                    'end_time(s)', value=1.5E-2,  min_value=0.0, step=0.001, format='%.3f')

        submit_button = st.form_submit_button('Submit')

        if submit_button:
            plate_model = PlateModel(**{'l_p': l_p,
                                        'w_p': w_p,
                                        'en1_p': en1_p,
                                        'en2_p': en2_p,
                                        'z_elv_p': z_elv_p,
                                        'move_x_p': move_x_p,
                                        'move_y_p': move_y_p,
                                        'rot_angle_p': rot_angle_p})

            box_model = BoxModel(**{'l_b': l_b,
                                    'w_b': w_b,
                                    'h_b': h_b,
                                    'en1_b': en1_b,
                                    'en2_b': en2_b,
                                    'en3_b': en3_b,
                                    'z_elv_b': z_elv_b,
                                    'move_x_b': move_x_b,
                                    'move_y_b': move_y_b,
                                    'rot_angle_b': rot_angle_b})

            crtl_params_model = CRTLParamsModel(**{'vz': vz, 'endtim': endtim})

            data = {**plate_model.dict(),
                    **box_model.dict(),
                    **crtl_params_model.dict()}

            bucket_name = st.secrets['bucket_name']
            my_s3 = get_my_s3()
            s3_client = my_s3.get_s3_client()

            s = BytesIO(json.dumps(data).encode('utf-8'))
            # https://stackoverflow.com/questions/26879981/writing-then-reading-in-memory-bytes-bytesio-gives-a-blank-result
            s.seek(0)

            filename = 'input_data.json'
            s3_client.upload_fileobj(Fileobj=s,
                                     Bucket=st.secrets['bucket_name'],
                                     Key=filename,
                                     ExtraArgs={'ACL': 'public-read'})
            now = datetime.now().strftime('%Y%m%d_%H%M%s')
            st.info(
                f'{filename} is uploaded to Bucket[{bucket_name}] at {now}.')


if __name__ == '__main__':
    main()
