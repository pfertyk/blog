Title: Recover encrypted home folder in Ubuntu
Date: 2017-04-26
Summary: When you forget your password, but still have the mount passphrase
Tags: linux, ecryptfs

Let's say you have an old computer with Ubuntu (or any of it's flavors).
You forgot the password, but you have the passphrase.
You want to recover the encrypted home folder. Here is how to do it.

You will need a Live USB distribution. I used Xubuntu, but the process should be
similar for other distros.

## Approach #1: ecryptfs-recover-private (not brilliant)

```text
xubuntu@xubuntu:~$ sudo ecryptfs-recover-private
INFO: Searching for encrypted private directories (this might take a while)...
find: ‘/run/user/999/gvfs’: Permission denied
find: File system loop detected; ‘/sys/kernel/debug/pinctrl’ is part of the same file system loop as ‘/sys/kernel/debug’.
```

```text
xubuntu@xubuntu:~$ sudo chroot /media/xubuntu/c1ecb1af-7c15-470f-a777-48ed5eb60247/
root@xubuntu:/# ecryptfs-recover-private 
INFO: Searching for encrypted private directories (this might take a while)...
INFO: Found [/home/.ecryptfs/pawel/.Private].
Try to recover this directory? [Y/n]:
/usr/bin/ecryptfs-recover-private: 63: /usr/bin/ecryptfs-recover-private: cannot create /dev/null: Permission denied
INFO: Found your wrapped-passphrase
Do you know your LOGIN passphrase? [Y/n] n
INFO: To recover this directory, you MUST have your original MOUNT passphrase.
INFO: When you first setup your encrypted private directory, you were told to record
INFO: your MOUNT passphrase.
INFO: It should be 32 characters long, consisting of [0-9] and [a-f].

Enter your MOUNT passphrase:
INFO: Success!  Private data mounted at [/tmp/ecryptfs.z7cibvV4].
```

![Encrypted filenames]({filename}/images/ecryptfs-encrypted-filenames.png)



## Approach #2: mount -t ecryptfs (working)

```text
xubuntu@xubuntu:~$ sudo ecryptfs-add-passphrase --fnek
Passphrase: 
Inserted auth tok with sig [9b15cb67b475a9e1] into the user session keyring
Inserted auth tok with sig [d06fa6176f780bdb] into the user session keyring
```

The important key is `d06fa6176f780bdb`.

```text
xubuntu@xubuntu:~$ sudo mount -t ecryptfs /media/xubuntu/c1ecb1af-7c15-470f-a777-48ed5eb60247/home/.ecryptfs/pawel/.Private/ /mnt
Passphrase: 
Select cipher: 
 1) aes: blocksize = 16; min keysize = 16; max keysize = 32
 2) blowfish: blocksize = 8; min keysize = 16; max keysize = 56
 3) des3_ede: blocksize = 8; min keysize = 24; max keysize = 24
 4) twofish: blocksize = 16; min keysize = 16; max keysize = 32
 5) cast6: blocksize = 16; min keysize = 16; max keysize = 32
 6) cast5: blocksize = 8; min keysize = 5; max keysize = 16
Selection [aes]: 
Select key bytes: 
 1) 16
 2) 32
 3) 24
Selection [16]: 
Enable plaintext passthrough (y/n) [n]: 
Enable filename encryption (y/n) [n]: y
Filename Encryption Key (FNEK) Signature [9b15cb67b475a9e1]: d06fa6176f780bdb
Attempting to mount with the following options:
  ecryptfs_unlink_sigs
  ecryptfs_fnek_sig=d06fa6176f780bdb
  ecryptfs_key_bytes=16
  ecryptfs_cipher=aes
  ecryptfs_sig=9b15cb67b475a9e1
Mounted eCryptfs
```

## Approach #3: changing the password (would be perfect)

As far as I know, it is not working.
