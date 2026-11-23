
void FUN_007de4a0(long param_1,uint param_2)

{
  long lVar1;
  ulong uVar2;
  
  if (*(uint *)(FUN_000025b0 + param_1 + 4) != param_2) {
    uVar2 = (ulong)param_2;
    lVar1 = param_1 + 0x25d8;
    FUN_00f819f0(lVar1,(&DAT_015d16c4)[uVar2 * 0x24]);
    FUN_00f81a10(lVar1,*(undefined4 *)(&DAT_015d16c8 + uVar2 * 0x24),
                 *(undefined4 *)(&DAT_015d16d0 + uVar2 * 0x24),
                 *(undefined4 *)(&DAT_015d16cc + uVar2 * 0x24));
    FUN_00f81a30(lVar1,*(undefined4 *)(&DAT_015d16d4 + uVar2 * 0x24),
                 *(undefined4 *)(&DAT_015d16dc + uVar2 * 0x24),
                 *(undefined4 *)(&DAT_015d16d8 + uVar2 * 0x24));
    FUN_00f7e410(lVar1,1);
    FUN_00f7e7c0(*(undefined8 *)(param_1 + 0x50),0,*(undefined4 *)(param_1 + 0x25d8));
    FUN_00f7e7c0(*(undefined8 *)(param_1 + 0x50),1,*(undefined4 *)(param_1 + 0x25d8));
    FUN_00f7e7c0(*(undefined8 *)(param_1 + 0x50),2,*(undefined4 *)(param_1 + 0x25d8));
    FUN_00f7e7c0(*(undefined8 *)(param_1 + 0x50),3,*(undefined4 *)(param_1 + 0x25d8));
    FUN_00f7e740(*(undefined8 *)(param_1 + 0x50),*(undefined4 *)(&DAT_015d16e0 + uVar2 * 0x24));
    *(uint *)(FUN_000025b0 + param_1 + 4) = param_2;
  }
  return;
}

