#!/usr/bin/env python3

import array, argparse, struct, fcntl, os, sys, ioctl_opt, ctypes, uuid, math
from collections import namedtuple
from pprint import pprint

#/*
# * Superblock - on disk version.  Must match the in core version above.
# * Must be padded to 64 bit alignment.
# */
#typedef struct xfs_dsb {
#    __be32		sb_magicnum;	/* magic number == XFS_SB_MAGIC */
#    __be32		sb_blocksize;	/* logical block size, bytes */
#    __be64		sb_dblocks;	/* number of data blocks */
#    __be64		sb_rblocks;	/* number of realtime blocks */
#    __be64		sb_rextents;	/* number of realtime extents */
#    uuid_t		sb_uuid;	/* file system unique id */
#    __be64		sb_logstart;	/* starting block of log if internal */
#    __be64		sb_rootino;	/* root inode number */
#    __be64		sb_rbmino;	/* bitmap inode for realtime extents */
#    __be64		sb_rsumino;	/* summary inode for rt bitmap */
#    __be32		sb_rextsize;	/* realtime extent size, blocks */
#    __be32		sb_agblocks;	/* size of an allocation group */
#    __be32		sb_agcount;	/* number of allocation groups */
#    __be32		sb_rbmblocks;	/* number of rt bitmap blocks */
#    __be32		sb_logblocks;	/* number of log blocks */
#    __be16		sb_versionnum;	/* header version == XFS_SB_VERSION */
#    __be16		sb_sectsize;	/* volume sector size, bytes */
#    __be16		sb_inodesize;	/* inode size, bytes */
#    __be16		sb_inopblock;	/* inodes per block */
#    char		sb_fname[12];	/* file system name */
#    __u8		sb_blocklog;	/* log2 of sb_blocksize */
#    __u8		sb_sectlog;	/* log2 of sb_sectsize */
#    __u8		sb_inodelog;	/* log2 of sb_inodesize */
#    __u8		sb_inopblog;	/* log2 of sb_inopblock */
#    __u8		sb_agblklog;	/* log2 of sb_agblocks (rounded up) */
#    __u8		sb_rextslog;	/* log2 of sb_rextents */
#    __u8		sb_inprogress;	/* mkfs is in progress, don't mount */
#    __u8		sb_imax_pct;	/* max % of fs for inode space */
#		    /* statistics */
#    /*
#     * These fields must remain contiguous.  If you really
#     * want to change their layout, make sure you fix the
#     * code in xfs_trans_apply_sb_deltas().
#     */
#    __be64		sb_icount;	/* allocated inodes */
#    __be64		sb_ifree;	/* free inodes */
#    __be64		sb_fdblocks;	/* free data blocks */
#    __be64		sb_frextents;	/* free realtime extents */
#    /*
#     * End contiguous fields.
#     */
#    __be64		sb_uquotino;	/* user quota inode */
#    __be64		sb_gquotino;	/* group quota inode */
#    __be16		sb_qflags;	/* quota flags */
#    __u8		sb_flags;	/* misc. flags */
#    __u8		sb_shared_vn;	/* shared version number */
#    __be32		sb_inoalignmt;	/* inode chunk alignment, fsblocks */
#    __be32		sb_unit;	/* stripe or raid unit */
#    __be32		sb_width;	/* stripe or raid width */
#    __u8		sb_dirblklog;	/* log2 of dir block size (fsbs) */
#    __u8		sb_logsectlog;	/* log2 of the log sector size */
#    __be16		sb_logsectsize;	/* sector size for the log, bytes */
#    __be32		sb_logsunit;	/* stripe unit size for the log */
#    __be32		sb_features2;	/* additional feature bits */
#    /*
#     * bad features2 field as a result of failing to pad the sb
#     * structure to 64 bits. Some machines will be using this field
#     * for features2 bits. Easiest just to mark it bad and not use
#     * it for anything else.
#     */
#    __be32	sb_bad_features2;
#
#    /* must be padded to 64 bit alignment */
#} xfs_dsb_t;
#

BLKGETSIZE64 = ioctl_opt.IOR(0x12, 114, ctypes.c_size_t)
BLKSSZGET  = ioctl_opt.IO(0x12, 104)
XFS_SDB_T_STRUCT = struct.Struct(">4sIQQQ16sQQQQIIIIIHHHH12sBBBBBBBBQQQQQQHBBIIIBBHIII") # Always big-endian per above struct
XFSSdbT = namedtuple("XFSSdbT",
                      ["sb_magicnum", "sb_blocksize", "sb_dblocks", "sb_rblocks", "sb_rextents",
                       "sb_uuid", "sb_logstart", "sb_rootino", "sb_rbmino", "sb_rsumino",
                       "sb_rextsize", "sb_agblocks", "sb_agcount", "sb_rbmblocks", "sb_logblocks",
                       "sb_versionnum", "sb_sectsize", "sb_inodesize", "sb_inopblock", "sb_fname",
                       "sb_blocklog", "sb_sectlog", "sb_inodelog", "sb_inopblog", "sb_agblklog",
                       "sb_rextslog", "sb_inprogress", "sb_imax_pct", "sb_icount", "sb_ifree",
                       "sb_fdblocks", "sb_frextents", "sb_uquotino", "sb_gquotino", "sb_qflags",
                       "sb_flags", "sb_shared_vn", "sb_inoalignmt", "sb_unit", "sb_width",
                       "sb_dirblklog", "sb_logsectlog", "sb_logsectsize", "sb_logsunit",
                       "sb_features2", "sb_bad_features2"])

def process_sector(sector):
    found = None
    if sector[:4] == b'XFSB':
        print("Found something that looks like XFS")
        xfs_sdb = XFSSdbT(*XFS_SDB_T_STRUCT.unpack(sector[:XFS_SDB_T_STRUCT.size]))
        xfs_sdb = xfs_sdb._replace(sb_uuid=uuid.UUID(bytes=xfs_sdb.sb_uuid))
        found = xfs_sdb
        if 2 ** xfs_sdb.sb_blocklog != xfs_sdb.sb_blocksize:
            print("sb_blocksize log mismatch!")
            found = None
        if 2 ** xfs_sdb.sb_sectlog != xfs_sdb.sb_sectsize:
            print("sb_sectsize log mismatch!")
            found = None
        if 2 ** xfs_sdb.sb_inodelog != xfs_sdb.sb_inodesize:
            print("sb_inodesize log mismatch!")
            found = None
        if 2 ** xfs_sdb.sb_inopblog != xfs_sdb.sb_inopblock:
            print("sb_inopblock log mismatch!")
            found = None
        if xfs_sdb.sb_agblklog != round(math.log(xfs_sdb.sb_agblocks, 2)):
            print("sb_agblocks log mismatch!")
            found = None
    return found

def main():
    parser = argparse.ArgumentParser("XFS partition extraction utility")
    parser.add_argument("-d", "--device", required=True, help="raw device to search for XFS partitions")
    parser.add_argument("-b", "--blocks", type=int, default=16384 * 16, help="read this many sectors at a time")
    args = parser.parse_args()
    print("Opening device %s" % args.device)
    with open(args.device, "rb", buffering=0) as dev_f:

        # Determine device sector size
        r = array.array("Q", [0])
        fcntl.ioctl(dev_f, BLKGETSIZE64, r)
        blk_dev_size = r[0]
        print("Device size:\t\t%i" % blk_dev_size)
        r = array.array("I", [0])
        fcntl.ioctl(dev_f, BLKSSZGET, r)
        blk_sector_size = r[0]
        print("Device sector size:\t%i" % blk_sector_size)
        num_sectors = blk_dev_size / blk_sector_size
        print("Device sector count:\t%i" % num_sectors)

        # Allocate buffer
        buf = bytearray(blk_sector_size * args.blocks)
        bytes_read = 0

        current_sector_no = 0

        while True:
            bytes_read_last = dev_f.readinto(buf)
            if not bytes_read_last:
                break

            bytes_read += bytes_read_last

            with memoryview(buf) as rbuf:
                while rbuf:
                    sector = rbuf[:blk_sector_size]
                    rbuf = rbuf[blk_sector_size:]
                    xfs_sdb = process_sector(sector)
                    if xfs_sdb:
                        print("XFS found:\tlosetup -o %i --sizelimit %i -b %i -r -f %s" % (current_sector_no * blk_sector_size,
                                                                                           xfs_sdb.sb_dblocks * xfs_sdb.sb_blocksize,
                                                                                           blk_sector_size,
                                                                                           args.device))
                        pprint(xfs_sdb._asdict())
                        seek_offset = current_sector_no * blk_sector_size + xfs_sdb.sb_dblocks * xfs_sdb.sb_blocksize
                        print("Seeking to sector:\t%i" % (seek_offset / blk_sector_size))
                        dev_f.seek(seek_offset)
                        current_sector_no = int(dev_f.tell() / blk_sector_size)
                        break
                    current_sector_no += 1

    return 0

if __name__ == "__main__":
    main()
