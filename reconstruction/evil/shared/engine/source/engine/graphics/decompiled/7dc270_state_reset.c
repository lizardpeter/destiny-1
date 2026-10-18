
void FUN_007dc270(long param_1,char param_2)

{
  long lVar1;
  long lVar2;
  int iVar3;
  int iVar4;
  
  *(undefined8 *)(param_1 + 0x1d28) = 1;
  *(undefined8 *)(param_1 + 0x1d20) = 1;
  *(undefined8 *)(param_1 + 0x1d38) = 1;
  *(undefined8 *)(param_1 + 0x1d40) = 1;
  *(undefined8 *)(param_1 + 0x1d30) = 1;
  *(undefined8 *)(param_1 + 0x1d48) = 1;
  *(undefined8 *)(param_1 + 0x1d50) = 1;
  lVar2 = 0;
  *(undefined1 *)(param_1 + 0x25c4) = 0;
  *(undefined4 *)(&DAT_000025cc + param_1) = 0;
  *(undefined4 *)(&DAT_000025c8 + param_1) = 0;
  *(undefined8 *)(param_1 + 0x1d60) = 0;
  do {
    *(undefined4 *)(param_1 + 0x1d78 + lVar2 * 4) = 0xffffffff;
    *(undefined4 *)(&DAT_00001df8 + lVar2 * 4 + param_1) = 0;
    lVar2 = lVar2 + 1;
  } while ((int)lVar2 != 0x20);
  thunk_FUN_012aa986(&DAT_00001e78 + param_1,0,0x700);
  *(undefined4 *)(param_1 + 0x1d68) = 0xffffffff;
  *(undefined8 *)(param_1 + 0x1d70) = 0;
  *(undefined4 *)(&DAT_000025a8 + param_1) = 0xfffffff;
  *(undefined4 *)(FUN_000025b0 + param_1 + 4) = 0;
  *(undefined4 *)(&DAT_000025c8 + param_1) = 0;
  *(undefined1 *)(param_1 + 0x25c4) = 0;
  *(undefined8 *)(param_1 + 0x25bc) = 0;
  *(undefined4 *)(&DAT_000025cc + param_1) = 0x3f800000;
  *(undefined4 *)(FUN_000025f0 + param_1) = 0;
  if (param_2 != '\0') {
    FUN_00992780(FUN_000025d0 + param_1);
    FUN_00f81a70(param_1 + 0x25d4);
    FUN_00992780(param_1 + 0x25d8);
    FUN_00992780(param_1 + 0x25dc);
    FUN_00992780(param_1 + 0x25e0);
    *(undefined4 *)(param_1 + 0x25e4) = 0;
    *(undefined4 *)(param_1 + 0x25b8) = 0;
    *(undefined4 *)(&DAT_000025e8 + param_1) = 0xffffffff;
  }
  *(undefined1 *)(param_1 + 0x27c0) = 0;
  lVar2 = *(long *)(param_1 + 0x50);
  if (lVar2 != 0) {
    iVar4 = 0;
    FUN_00f8f0e0(lVar2,0,0);
    FUN_00f8f0e0(lVar2,1,0);
    FUN_00f8f0e0(lVar2,2,0);
    FUN_00f8f0e0(lVar2,3,0);
    FUN_00f7eec0(lVar2,0);
    FUN_00f7f790(lVar2,0);
    FUN_00f7f840(lVar2,0);
    FUN_00f80730(lVar2,0xffff);
    FUN_00f7f7e0(lVar2,0);
    lVar1 = lVar2 + 0xc0;
    FUN_00f8b790(lVar1,0,0,0);
    FUN_00f8b8c0(lVar1,0);
    FUN_00f8b500(lVar1,2,0,1,0);
    *(undefined4 *)(lVar2 + 0x3a8) = *(undefined4 *)(FUN_000025f0 + param_1);
    FUN_00f7fe20(lVar2);
    FUN_00f806d0(lVar2,*(undefined1 *)(param_1 + 0x27c0));
    iVar3 = 0;
    do {
      FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,0,iVar3,1,0);
      iVar3 = iVar3 + 1;
    } while (iVar3 != 0x10);
    do {
      FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,1,iVar4,1,0);
      iVar4 = iVar4 + 1;
    } while (iVar4 != 0x10);
    iVar3 = 0;
    do {
      FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,2,iVar3,1,0);
      iVar3 = iVar3 + 1;
    } while (iVar3 != 0x10);
    iVar3 = 0;
    do {
      FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,3,iVar3,1,0);
      iVar3 = iVar3 + 1;
    } while (iVar3 != 0x10);
    iVar3 = 0;
    do {
      FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,4,iVar3,1,0);
      iVar3 = iVar3 + 1;
    } while (iVar3 != 0x10);
    iVar3 = 0;
    do {
      FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,5,iVar3,1,0);
      iVar3 = iVar3 + 1;
    } while (iVar3 != 0x10);
    iVar3 = 0;
    do {
      FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,6,iVar3,1,0);
      iVar3 = iVar3 + 1;
    } while (iVar3 != 0x10);
    iVar4 = 0;
    iVar3 = 0;
    do {
      FUN_00f8b410(*(long *)(param_1 + 0x50) + 0xc0,0,iVar4,1,0);
      iVar4 = iVar4 + 1;
    } while (iVar4 != 0x10);
    do {
      FUN_00f8b410(*(long *)(param_1 + 0x50) + 0xc0,1,iVar3,1,0);
      iVar3 = iVar3 + 1;
    } while (iVar3 != 0x10);
    iVar3 = 0;
    do {
      FUN_00f8b410(*(long *)(param_1 + 0x50) + 0xc0,2,iVar3,1,0);
      iVar3 = iVar3 + 1;
    } while (iVar3 != 0x10);
    iVar3 = 0;
    do {
      FUN_00f8b410(*(long *)(param_1 + 0x50) + 0xc0,3,iVar3,1,0);
      iVar3 = iVar3 + 1;
    } while (iVar3 != 0x10);
    iVar3 = 0;
    do {
      FUN_00f8b410(*(long *)(param_1 + 0x50) + 0xc0,4,iVar3,1,0);
      iVar3 = iVar3 + 1;
    } while (iVar3 != 0x10);
    iVar3 = 0;
    do {
      FUN_00f8b410(*(long *)(param_1 + 0x50) + 0xc0,5,iVar3,1,0);
      iVar3 = iVar3 + 1;
    } while (iVar3 != 0x10);
    iVar3 = 0;
    do {
      FUN_00f8b410(*(long *)(param_1 + 0x50) + 0xc0,6,iVar3,1,0);
      iVar3 = iVar3 + 1;
    } while (iVar3 != 0x10);
  }
  return;
}

