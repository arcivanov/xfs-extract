## XFS Extract

Scans the raw disk to allow extraction. The utility itself doesn't modify the disk and only opens files for reading.

Root privileges required.

If the XFS file system is corrupted then your ability to mount it and extract data from it will vary depending on 
the level of the corruption.

## Requirements

pip install ioctl_opt

## Installation

```
$ python3 -m venv xfs-extract
$ xfs-extract/bin/pip install ioctl_opt
$ sudo xfs-extract/bin/python xfs-extract.py --help
usage: XFS partition extraction utility [-h] -d DEVICE [-b BLOCKS]

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        raw device to search for XFS partitions
  -b BLOCKS, --blocks BLOCKS
                        read this many sectors at a time
```

## How To Use

1. Run `xfs-extract`. See below.
2. Mount each `XFS found: ` mount a loop device, e.g. `sudo losetup -o 2097152 --sizelimit 214748364800 -b 512 -r -f /dev/nvme0n1`
3. Mount XFS via loop device, e.g. `mount -o ro /dev/loop1 /mnt/disk1`

Here's the sample output of the output that you may receive. 
```
$ sudo xfs-extract/bin/python xfs-extract.py -d /dev/nvme0n1
Opening device /dev/nvme0n1
Device size:            512110190592
Device sector size:     512
Device sector count:    1000215216
Found something that looks like XFS
XFS found:      losetup -o 2097152 --sizelimit 214748364800 -b 512 -r -f /dev/nvme0n1
OrderedDict([('sb_magicnum', b'XFSB'),
             ('sb_blocksize', 4096),
             ('sb_dblocks', 52428800),
             ('sb_rblocks', 0),
             ('sb_rextents', 0),
             ('sb_uuid', UUID('4c846438-668e-4d10-a853-4b92a48c8603')),
             ('sb_logstart', 33554437),
             ('sb_rootino', 128),
             ('sb_rbmino', 129),
             ('sb_rsumino', 130),
             ('sb_rextsize', 1),
             ('sb_agblocks', 13107200),
             ('sb_agcount', 4),
             ('sb_rbmblocks', 0),
             ('sb_logblocks', 25600),
             ('sb_versionnum', 46245),
             ('sb_sectsize', 512),
             ('sb_inodesize', 512),
             ('sb_inopblock', 8),
             ('sb_fname', b'docker\x00\x00\x00\x00\x00\x00'),
             ('sb_blocklog', 12),
             ('sb_sectlog', 9),
             ('sb_inodelog', 9),
             ('sb_inopblog', 3),
             ('sb_agblklog', 24),
             ('sb_rextslog', 0),
             ('sb_inprogress', 0),
             ('sb_imax_pct', 25),
             ('sb_icount', 8640),
             ('sb_ifree', 145),
             ('sb_fdblocks', 52298246),
             ('sb_frextents', 0),
             ('sb_uquotino', 18446744073709551615),
             ('sb_gquotino', 18446744073709551615),
             ('sb_qflags', 0),
             ('sb_flags', 0),
             ('sb_shared_vn', 0),
             ('sb_inoalignmt', 8),
             ('sb_unit', 0),
             ('sb_width', 0),
             ('sb_dirblklog', 0),
             ('sb_logsectlog', 0),
             ('sb_logsectsize', 0),
             ('sb_logsunit', 1),
             ('sb_features2', 394),
             ('sb_bad_features2', 394)])
Seeking to sector:      419434496
```
