
ulong FUN_0090ee70(undefined4 param_1,long param_2)

{
  undefined8 *puVar1;
  long lVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 *puVar5;
  char cVar6;
  uint uVar7;
  int iVar8;
  undefined4 uVar9;
  long lVar10;
  undefined8 uVar11;
  ulong uVar12;
  long lVar13;
  undefined8 local_78;
  undefined8 local_70;
  long local_68;
  long local_60;
  long local_58;
  long local_50;
  undefined8 local_48;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar6 = '\0';
  if ((char)DAT_0273ea90[0x2a] != '\0') {
    local_78 = *(undefined8 *)((long)DAT_0273ea90 + 0xa9);
    if ((char)DAT_0273ea90[0x2a] != '\0') {
      cVar6 = FUN_000685a0(param_2 + 0xc,&local_78);
    }
  }
  local_70 = *(undefined8 *)(param_2 + 0xc);
  local_68 = *(long *)(param_2 + 0x28);
  local_58 = *(long *)(param_2 + 0x98);
  local_50 = *(long *)(param_2 + 0xa0);
  local_48 = *(undefined8 *)(param_2 + 0x20);
  local_40 = *(undefined8 *)(param_2 + 0x18);
  local_60 = local_50;
  if (local_50 == 0) {
    local_60 = local_68;
  }
  uVar7 = FUN_00074930(DAT_0273ea80,param_1);
  iVar8 = FUN_00302640(param_1,cVar6,(ulong)uVar7,&local_70);
  if (iVar8 == -1) {
    if (uVar7 != 0xffffffff) {
      FUN_00074760(DAT_0273ea80,uVar7);
    }
  }
  else if (uVar7 == 0xffffffff) {
    FUN_00302a60(iVar8);
  }
  else {
    lVar2 = *(long *)(DAT_0273ea80 + 8);
    lVar13 = ((ulong)uVar7 & 0xffff) * 0x2af0;
    *(int *)(lVar2 + 4 + lVar13) = iVar8;
    *(undefined4 *)(lVar2 + 0x284c + lVar13) = 0xffffffff;
    *(undefined4 *)(lVar2 + 0x2850 + lVar13) = 0xffffffff;
    *(undefined4 *)(lVar2 + 0x2854 + lVar13) = 0xffffffff;
    *(undefined4 *)(lVar2 + 0x2864 + lVar13) = 0xffffffff;
    *(undefined8 *)(lVar2 + 0x285c + lVar13) = 0xffffffffffffffff;
    uVar9 = FUN_0063fcd0();
    *(undefined4 *)(lVar2 + 0x2858 + lVar13) = uVar9;
    FUN_0090f180(uVar7,1,param_2);
    *(undefined4 *)(lVar2 + 8 + lVar13) = 0xffffffff;
    puVar5 = DAT_0273eaa0;
    if (cVar6 != '\0') {
      if (*(int *)((long)DAT_0273eaa0 + 0xe4) == 2) {
        lVar10 = FUN_0034e3c0();
        if (*(char *)(lVar10 + 0xa4) != '\0') {
          *(undefined4 *)(lVar2 + 0x38 + lVar13) = *(undefined4 *)(puVar5 + 0x1c);
          thunk_FUN_012aa7c6(lVar2 + 0x2870 + lVar13,puVar5 + 5,0xb8);
          if (*(char *)(puVar5 + 4) != '\0') {
            uVar11 = *puVar5;
            uVar3 = puVar5[1];
            uVar4 = puVar5[3];
            puVar1 = (undefined8 *)(lVar2 + 0x70 + lVar13);
            *puVar1 = puVar5[2];
            puVar1[1] = uVar4;
            puVar1 = (undefined8 *)(lVar2 + 0x60 + lVar13);
            *puVar1 = uVar11;
            puVar1[1] = uVar3;
          }
        }
      }
      thunk_FUN_012aa986(puVar5,0,0xf0);
    }
    if (*(char *)(param_2 + 1) == '\0') {
      *DAT_0273ea90 = *DAT_0273ea90 + 1;
      FUN_00b9f2c0(uVar7);
      FUN_0090a2c0(uVar7);
    }
    if (local_58 != 0) {
      cVar6 = FUN_005428c0();
      if (cVar6 != '\0') {
        uVar11 = FUN_0056b260();
        if (local_58 != 0) {
          uVar9 = FUN_00001df0(uVar11);
          lVar10 = FUN_0056dc00(uVar11,2,uVar9,&local_58);
          if (lVar10 != 0) {
            FUN_00065a00(lVar2 + 0x2ab0 + lVar13,lVar10 + 0x10,0x1b);
            FUN_00065a00(lVar2 + 0x2ae6 + lVar13,lVar10 + 0x46,5);
          }
        }
      }
    }
    thunk_FUN_003f47e0(iVar8);
  }
  if (*DAT_01a1f100 == local_38) {
    return (ulong)uVar7;
  }
  uVar12 = thunk_FUN_012aa7f6();
  return uVar12;
}

