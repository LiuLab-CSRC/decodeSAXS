import sys
import zalign
#from sastbx.zernike_model import model_interface

#pdbpath=sys.argv[1]

pdbfile = '/root/sites/hhe-site/decodeSAXS/reconstruction_web/media/result/1561688269/out.ccp4'
#cavitymodel = model_interface.build_model(pdbfile, 'pdb', 20, None)
#shiftrmax=cavitymodel.rmax*0.9
shiftrmax=90
args = ['fix=/root/sites/hhe-site/decodeSAXS/reconstruction_web/media/result/1561688269/out.ccp4', 'typef=ccp4', 'mov=/root/sites/hhe-site/decodeSAXS/reconstruction_web/media/result/1561688269/upload_pdb.pdb', 'rmax=%f'%shiftrmax]
zalign.run(args, '/root/sites/hhe-site/decodeSAXS/reconstruction_web/media/result/1561688269')