#!/usr/bin/python
import sys
import os
import math

schemes = [
        #'UnsafeBaseline',
        'SpectreSafeInvisibleSpec',
        'FuturisticSafeInvisibleSpec',
        ]

isas = [
        'arm',
        #'x86'
        ]
num_cpus = num_threads = [
        #'4',
        '8',
        #'16',
        #'64',
        ]

data_size = 'simmedium'
runtype = 'restore' #'ckpts'
test_case = 'InvisiSpec-upto-until-end-of-roi'
#test_case = 'InvisiSpec-upto-100m-optimized'
#test_case = 'test-specloads-invisi'

m5_root = '/data/sungkeun/HWSecurity/m5out'

benches = [
            'blackscholes',
            #'bodytrack',
            'canneal',
            'dedup',
            'facesim',
            'ferret',      # Segmentation fault with 16, 64 cpus
            'fluidanimate',
            'freqmine',
            'streamcluster',
            'swaptions',
            #'vips',
            'x264',
            ]
os.environ["GEM5_PATH"] = "./"

def create_command(bench,
        num_cpu, num_thread,
        data_size, scheme,
        isa, runtype):
    gem5_options = []
    script_options = []

    if isa == 'x86':
        os.environ['M5_PATH'] = '/home/sungkeun/gem5-kernel/x86_parsec'

        gem5_options.append(('bin-path'    ,
            './build/X86_MESI_Two_Level/gem5.fast'))

        script_options.append(('--script',
            ('./scripts_x86/%s_%sc_%s_ckpts.rcS' % \
                    (bench, num_thread, data_size))))

        script_options.append(('--kernel',
            os.environ['M5_PATH'] + \
                    '/binaries/x86_64-vmlinux-2.6.28.4-smp'))

        script_options.append(('--disk-image',
            os.environ['M5_PATH'] + \
                    '/disks/x86root-parsec.img'))
    elif isa == 'arm':
        os.environ['M5_PATH'] = '/home/sungkeun/gem5-kernel/arm_parsec'
        gem5_options.append(('bin-path',
            './build/ARM_MESI_Two_Level/gem5.fast'))

        script_options.append(('--script',
            ('./scripts/%s_%s_%s.rcS' % (bench, data_size, num_thread))))

        script_options.append(('--kernel',
            os.environ['M5_PATH'] + \
                    '/binaries/vmlinux.aarch64.20140821'))

        script_options.append(('--disk-image',
            os.environ['M5_PATH'] + \
                    '/disks/parsec-aarch64-ubuntu-trusty-headless.img'))

        script_options.append(('--dtb-file',
            os.environ['M5_PATH'] + \
                    '/binaries/vexpress.aarch64.20140821.dtb'))
        script_options.append(('--machine-type',
            'VExpress_EMM64'))
    else:
        print ("unknown isa" + isa)
        exit()

    if runtype == 'restore':
        gem5_options.append(('--outdir',
            ('%s/restore/%s/%s-%s-%s-%s-%s' % \
                (m5_root, test_case, bench, \
                num_cpu, data_size, isa, scheme))))
        outdir = '%s/restore/%s/%s-%s-%s-%s-%s' % \
                (m5_root, test_case, bench, \
                num_cpu, data_size, isa, scheme)
        script_options.append(('--cpu-type', 'DerivO3CPU'))
        script_options.append(('--checkpoint-dir',
            ('%s/ckpts/%s-%s-%s-%s' % (m5_root, bench, \
                    num_cpu, data_size, isa))))
        script_options.append(('--checkpoint-restore', '1'))

    elif runtype == 'ckpts':
        gem5_options.append(('--outdir',
            ('%s/ckpts/%s-%s-%s-%s' % (m5_root, bench, \
                    num_cpu, data_size, isa))))
        outdir = '%s/ckpts/%s-%s-%s-%s' % \
                (m5_root, bench, num_cpu, data_size, isa)
        script_options.append(('--cpu-type',
            'AtomicSimpleCPU'))
        script_options.append(('--checkpoint-dir',
            ('%s/ckpts/%s-%s-%s-%s' % \
                    (m5_root, bench, num_cpu, data_size, isa))))

    elif runtype == 'full':
        gem5_options.append(('--outdir',
            ('%s/full/%s-%s-%s-%s-%s' % \
                    (m5_root, bench, num_cpu, data_size, isa, scheme))))
        outdir = '%s/full/%s-%s-%s-%s-%s' % \
                (m5_root, bench, num_cpu, data_size, isa, scheme)
        script_options.append(('--cpu-type',
            'DerivO3CPU'))
    else:
        print ("unknown runtype " + runtype)
        exit()

    # common options
    #gem5_options.append(('--debug-flags', 'NetworkDebug,ProtocolTrace'))
    #gem5_options.append(('--debug-flags', 'NetworkDebug'))
    #gem5_options.append(('--debug-flags', 'O3CPUAll'))
    #gem5_options.append(('--debug-file', 'debug.out'))
    #gem5_options.append(('--redirect-stdout', ''))
    #gem5_options.append(('--redirect-stderr', ''))
    script_options.insert(0,
            ('config', os.environ['GEM5_PATH'] + \
                    'configs/example/fs.py'))
    script_options.append(('--num-cpus', num_cpu))

    # memory options
    script_options.append(('--mem-size', '2GB'))
    if runtype == 'restore':
        script_options.append(('--ruby', ''))
        script_options.append(('--num-l2caches', num_cpu))
        script_options.append(('--num-dirs', num_cpu))
        script_options.append(('--l1d_assoc', '8'))
        script_options.append(('--l2_assoc', '16'))
        script_options.append(('--l1i_assoc', '4'))

        # NOC options
        script_options.append(('--network', 'garnet2.0'))
        script_options.append(('--topology', 'Mesh_XY'))

        if num_cpu == '8':
            mesh_rows = 4
        elif num_cpu == '64':
            mesh_rows = 8
        else:
            mesh_rows = int(math.log(int(num_cpu), 2))

        assert(type(mesh_rows) == int)
        script_options.append(('--mesh-rows', str(mesh_rows)))

        # InvisiSpec
        script_options.append(('--scheme', scheme))
        script_options.append(('--needsTSO', '1'))
        #script_options.append(('--maxinsts', '500000000'))


    return gem5_options, script_options, outdir


for bench in benches:
    for scheme in schemes:
        for isa in isas:
            for num_cpu in num_cpus:

                gem5_opts, script_opts, outdir = \
                        create_command(bench, \
                        num_cpu, num_cpu, data_size, \
                        scheme, isa, runtype);
                command = ''
                debug_command = ''

                for opts in [gem5_opts, script_opts]:
                    for opt, val in opts:
                        # manage single value options
                        if opt in ['bin-path', 'config']:
                            command += val + ' '
                            debug_command += val + '\n'
                        elif opt in ['--ruby', '--redirect-stdout', \
                                '--redirect-stderr']:
                            command += opt + ' '
                            debug_command += opt + '\n'
                        else:
                            command += '%s=%s ' % (opt, val)
                            debug_command += '%s=%s\n' % (opt, val)

                        # create folder if this options specifies folder path
                        if opt in ['--outdir', '--checkpoint-dir']:
                            try:
                                os.makedirs(val)
                            except OSError:
                                None

                command += " > %s/log 2>&1 &" % (outdir)
                if runtype == 'ckpts':
                    if scheme == 'UnsafeBaseline':
                        print command
                        print '\n'
                        #os.system(command)
                else:
                    print command
                    print '\n'
                    #os.system(command)
