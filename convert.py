# -*- coding: utf-8 -*-
import numpy as np
import sys, os

def main():
    if len(sys.argv) < 3:
        print ("Error: supply 2 command line arguments, ./main.py [...].ascii path_to_potential")
        return 0
    
    spath = sys.argv[1]
    ppath = sys.argv[2]
    
    if not os.path.isfile(spath):
        print ("Error: Spilady ascii file %s not found." % spath)
        return 0
    
    # the potential file is not actually used
    if not os.path.isfile(ppath):
        print ("Warning: potential file %s not present at path." % ppath)
    
    prefix = os.path.basename(spath).split('.')[0] # get file prefix
    
    with open(spath, 'r') as rfile:
        sraw = rfile.read()
    
    sraw = [_row for _row in sraw.split('\n') if _row != '']
    sraw = [_row.split(' ') for _row in sraw]
    
    natoms = sraw[0][0]
    time = sraw[0][1]
    
    Lxx, Lyx, Lyy = sraw[1]
    Lzx, Lzy, Lzz = sraw[2]
    
    # get the masses from wiki or the potential file
    # to generalise, make atomids and atommass dictionaries of potentialfiles 
    atomids  = {'Fe': '1', 'Ni': '2', 'Cr': '3'}
    atommass = {'1': 55.8450, '2': 58.69340, '3': 51.99610}

    sarray = np.r_[sraw[3:]]
    
    xyz   = sarray[:,:3]
    types = [atomids[_s] for _s in sarray[:,3]]
    vel   = sarray[:,4:] # proper conversion from spliday momenta to lammps velocity NYI; check units
    ids   = [x+1 for x in range(len(xyz))]
    
    # define the box as triclinic if any of the elements is above a tiny threshold
    if (np.abs(np.array([Lyx, Lzx, Lzy], dtype=np.float)) > 1e-8).any():
        triclinic = True
    else:
        triclinic = False
    
    
    ### WRITING DATA FILE ###
    with open('output/%s.data' % prefix, 'w') as efile:
        efile.write('LAMMPS data file converted from SPILDAY ascii file\n\n')

        efile.write('%s atoms\n' % natoms)
        efile.write('%s atom types\n\n' % np.unique(types).size)

        efile.write('0.0 %s xlo xhi\n' % Lxx)
        efile.write('0.0 %s ylo yhi\n' % Lyy)
        efile.write('0.0 %s zlo zhi\n' % Lzz)
        if triclinic:
            efile.write('%s %s %s xy xz yz\n' % (Lyx, Lzx, Lzy))
        efile.write('\n')

        efile.write('Masses\n\n')
        for _type in np.unique(types):
            efile.write('%s %f\n' % (_type, atommass[_type]))   
        efile.write('\n')  

        efile.write('Atoms # atomic\n\n')
        for i in range(len(xyz)):
            efile.write('%s %s %s %s %s 0 0 0\n' % (ids[i], types[i], xyz[i][0], xyz[i][1], xyz[i][2]))
        efile.write('\n')     

        efile.write('Velocities\n\n')
        for i in range(len(xyz)):
            efile.write('%s %s %s %s\n' % (ids[i], vel[i][0], vel[i][1], vel[i][2]))
      
    ### WRITING INPUT FILE ###
    potential_string = ' '.join([_key for _key in atomids if atomids[_key] in np.unique(types)])
    
    with open('output/%s.in' % prefix, 'w') as efile:
        efile.write('# LAMMPS input file for data file converted from SPILDAY ascii file\n\n')

        efile.write('units metal\n')
        efile.write('atom_style atomic\n')
        efile.write('units metal\n')
        efile.write('atom_modify map array sort 0 0.0\n')
        efile.write('boundary p p p\n\n')

        efile.write('read_data output/%s.data\n' % prefix)

        efile.write('pair_style eam/fs\n')
        efile.write('pair_coeff * * %s %s\n' % (ppath, potential_string))
        efile.write('neighbor 1.5 bin\n\n')

        # for writing out atomic energies
        efile.write('compute cpe all pe/atom\n')
        efile.write('compute cpetotal all reduce sum c_cpe\n\n')

        efile.write('thermo 100\n')
        efile.write('thermo_style custom step c_cpetotal press\n')
        efile.write('thermo_modify flush yes format float %23.16e\n\n')

        efile.write('minimize 1e-10 0 10000 10000\n\n')
        
        # important: write_dump first, write_data after; else computes wont be current
        efile.write('write_dump all custom %s.dump id type x y z c_cpe\n' % prefix)    
        efile.write('write_data relaxed_%s.data\n\n' % prefix)

    print ("Conversion complete, see output/%s.data and output/%s.in" % (prefix, prefix))    
    return 0

if __name__=="__main__":
    main()

