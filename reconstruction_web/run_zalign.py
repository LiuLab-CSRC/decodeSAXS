import argparse
import zalign
from sastbx.zernike_model import model_interface


parser=argparse.ArgumentParser()
parser.add_argument('--job_id',help='job id',type=str)
args=parser.parse_args()
pdbpath=args.job_id


pdbfile = './reconstruction_web/media/result/%s/out.ccp4'%pdbpath
cavitymodel = model_interface.build_model(pdbfile, 'pdb', 20, None)
shiftrmax=cavitymodel.rmax*0.9
args = ['fix=./reconstruction_web/media/result/%s/out.ccp4'%pdbpath, 'typef=ccp4', 'mov=./reconstruction_web/media/result/%s/upload_pdb.pdb'%pdbpath, 'rmax=%f'%shiftrmax]
zalign.run(args, './reconstruction_web/media/result/'+pdbpath)