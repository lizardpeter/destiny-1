
undefined8 FUN_006e4d70(uint *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  long lVar2;
  byte bVar3;
  char cVar4;
  uint uVar5;
  char *pcVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  uint uVar10;
  long lVar11;
  undefined8 uVar12;
  undefined8 local_88;
  undefined8 uStack_80;
  undefined8 local_78;
  uint local_70;
  long local_68;
  undefined8 local_50;
  undefined8 local_48;
  uint local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  pcVar6 = (char *)thunk_FUN_00326e00(param_2);
  if (2 < *(uint *)(pcVar6 + 4)) goto LAB_006e4fe8;
  uVar5 = FUN_0030ceb0(param_1);
  uVar10 = (int)*param_1 >> 0xd;
  lVar8 = (ulong)((uVar10 >> 0x12 | 0x3ff) & uVar10) * 0x40;
  lVar2 = *(long *)(param_1 + 2);
  lVar11 = *DAT_01a238a0;
  lVar9 = *(long *)(lVar11 + 0x10 + lVar8);
  uVar7 = (ulong)((*param_1 & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar8));
  lVar11 = (lVar9 + uVar7) - ((long)*(int *)(lVar11 + 0x34 + lVar8) & *(ulong *)(lVar9 + 8 + uVar7))
  ;
  if (pcVar6[1] == '\x01') {
    local_88 = 0;
    uStack_80 = 0;
    local_78 = 0;
    local_50 = *(undefined8 *)param_1;
    local_48 = *(undefined8 *)(param_1 + 2);
    local_40 = param_1[4];
    FUN_001d36a0(&local_50,*(undefined4 *)PTR_DAT_0191a888,lVar2 + 0xa8 + lVar11,&local_88);
    uVar1 = *(undefined4 *)PTR_DAT_0191a890;
    uVar12 = 1;
LAB_006e4ee3:
    FUN_0030c6a0(param_1,&local_88,uVar1,0,uVar12);
  }
  else if (*pcVar6 == '\x01') {
    FUN_006e3eb0(param_1);
    local_88 = 0;
    uStack_80 = 0;
    local_78 = 0;
    local_50 = *(undefined8 *)param_1;
    local_48 = *(undefined8 *)(param_1 + 2);
    local_40 = param_1[4];
    FUN_001d36a0(&local_50,*(undefined4 *)PTR_DAT_0191a888,lVar2 + 0xa8 + lVar11,&local_88);
    uVar1 = *(undefined4 *)PTR_DAT_0191a890;
    uVar12 = 0;
    goto LAB_006e4ee3;
  }
  if (pcVar6[1] == '\x01') {
    bVar3 = *(byte *)((long)param_1 + 0x1ad) | 1;
  }
  else {
    bVar3 = *(byte *)((long)param_1 + 0x1ad) & 0xfe;
  }
  *(byte *)((long)param_1 + 0x1ad) = bVar3;
  lVar2 = DAT_02692228;
  if (((*pcVar6 == '\0') && (pcVar6[1] != '\0')) && (uVar5 != 0xffffffff)) {
    uVar10 = (uVar5 & 0x1fff) * DAT_02692230;
    FUN_0061ed40(param_1 + 0xc,uVar5);
    cVar4 = FUN_00337fe0((ulong)uVar10 + lVar2,*(undefined4 *)PTR_DAT_019b4000,&local_88,0);
    uVar5 = 0xffffffff;
    if (cVar4 != '\0') {
      lVar9 = (ulong)(((uint)((int)local_70 >> 0xd) >> 0x12 | 0x3ff) & (int)local_70 >> 0xd) * 0x40;
      lVar2 = *DAT_01a238a0;
      lVar11 = *(long *)(lVar2 + 0x10 + lVar9);
      uVar7 = (ulong)((local_70 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar9));
      uVar5 = *(uint *)(local_68 + 0x24 +
                       ((lVar11 + uVar7) -
                       ((long)*(int *)(lVar2 + 0x34 + lVar9) & *(ulong *)(lVar11 + 8 + uVar7))));
    }
    param_1[0x66] = uVar5;
  }
  else if (pcVar6[1] == '\0') {
    param_1[0x66] = 0xffffffff;
    FUN_0061ed40(param_1 + 0xc,0xffffffff);
  }
LAB_006e4fe8:
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),1);
  }
  uVar12 = thunk_FUN_012aa7f6();
  return uVar12;
}

