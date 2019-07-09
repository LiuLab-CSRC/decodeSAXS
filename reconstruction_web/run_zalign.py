import sys
import zalign
from sastbx.zernike_model import model_interface

pdbpath=sys.argv[1]

pdbfile = '/root/sites/hhe-site/decodeSAXS/reconstruction_web/media/result/%s/out.ccp4'%pdbpath
cavitymodel = model_interface.build_model(pdbfile, 'ccp4', 20, None)
shiftrmax=cavitymodel.rmax*0.9
args = ['fix=/root/sites/hhe-site/decodeSAXS/reconstruction_web/media/result/%s/out.ccp4'%pdbpath, 'typef=ccp4', 'mov=/root/sites/hhe-site/decodeSAXS/reconstruction_web/media/result/%s/upload_pdb.pdb'%pdbpath, 'rmax=%f'%shiftrmax]
zalign.run(args, '/root/sites/hhe-site/decodeSAXS/reconstruction_web/media/result/%s'%pdbpath)