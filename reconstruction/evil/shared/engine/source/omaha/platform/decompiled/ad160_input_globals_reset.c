
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

ulong FUN_000ad160(void)

{
  uint uVar1;
  ulong uVar2;
  
  uVar1 = FUN_000f7c30();
  LOCK();
  if (DAT_01ad4850 != 0) {
    uVar1 = DAT_01ad4850;
  }
  DAT_01ad4850 = uVar1;
  UNLOCK();
  uVar2 = (ulong)DAT_01ad4840;
  thunk_FUN_012aa986(&DAT_01ad40e0 + uVar2 * 0x3b0,0,0x3b0);
  thunk_FUN_012aa986(&DAT_01ad40e0 + (uVar2 ^ 1) * 0x3b0,0,0x3b0);
  _DAT_01ad4870 = 0;
  _DAT_01ad4878 = 0;
  _DAT_01ad4860 = 0;
  uRam0000000001ad4868 = 0;
  _DAT_01ad4890 = 0;
  uRam0000000001ad4898 = 0;
  _DAT_01ad4880 = 0;
  uRam0000000001ad4888 = 0;
  _DAT_01ad48b0 = 0;
  uRam0000000001ad48b8 = 0;
  _DAT_01ad48a0 = 0;
  uRam0000000001ad48a8 = 0;
  _DAT_01ad48d0 = 0;
  uRam0000000001ad48d8 = 0;
  _DAT_01ad48c0 = 0;
  uRam0000000001ad48c8 = 0;
  _DAT_01ad48f0 = 0;
  uRam0000000001ad48f8 = 0;
  _DAT_01ad48e0 = 0;
  uRam0000000001ad48e8 = 0;
  _DAT_01ad4910 = 0;
  uRam0000000001ad4918 = 0;
  _DAT_01ad4900 = 0;
  uRam0000000001ad4908 = 0;
  _DAT_01ad4930 = 0;
  uRam0000000001ad4938 = 0;
  _DAT_01ad4920 = 0;
  uRam0000000001ad4928 = 0;
  _DAT_01ad4950 = 0;
  uRam0000000001ad4958 = 0;
  _DAT_01ad4940 = 0;
  uRam0000000001ad4948 = 0;
  _DAT_01ad4970 = 0;
  uRam0000000001ad4978 = 0;
  _DAT_01ad4960 = 0;
  uRam0000000001ad4968 = 0;
  _DAT_01ad4990 = 0;
  uRam0000000001ad4998 = 0;
  _DAT_01ad4980 = 0;
  _DAT_01ad4988 = 0;
  _DAT_01ad49b0 = 0;
  uRam0000000001ad49b8 = 0;
  _DAT_01ad49a0 = 0;
  _DAT_01ad49a8 = 0;
  _DAT_01ad49d0 = 0;
  uRam0000000001ad49d8 = 0;
  _DAT_01ad49c0 = 0;
  uRam0000000001ad49c8 = 0;
  _DAT_01ad49f0 = 0;
  uRam0000000001ad49f8 = 0;
  _DAT_01ad49e0 = 0;
  uRam0000000001ad49e8 = 0;
  _DAT_01ad4a10 = 0;
  _DAT_01ad4a08 = 0;
  _DAT_01ad4a00 = 0;
  uVar2 = FUN_000f7c30();
  LOCK();
  if ((uint)uVar2 == DAT_01ad4850) {
    DAT_01ad4850 = 0;
  }
  else {
    uVar2 = (ulong)DAT_01ad4850;
  }
  UNLOCK();
  return uVar2;
}

