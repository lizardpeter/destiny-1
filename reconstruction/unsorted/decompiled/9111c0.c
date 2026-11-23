
void FUN_009111c0(uint param_1,undefined8 *param_2,char param_3)

{
  undefined4 uVar1;
  undefined1 uVar2;
  undefined2 uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  undefined2 uVar6;
  undefined4 uVar7;
  int iVar8;
  undefined4 uVar9;
  long lVar10;
  undefined8 uVar11;
  char cVar12;
  char cVar13;
  int iVar14;
  long lVar15;
  undefined8 *puVar16;
  undefined8 *puVar17;
  long lVar18;
  int iVar19;
  undefined4 local_1130 [2];
  undefined4 local_1128 [2];
  long local_1120;
  undefined8 local_1118;
  undefined8 local_1110;
  undefined8 local_1108;
  undefined8 local_1100;
  undefined4 local_10f8;
  undefined8 local_10f0;
  undefined8 local_10e8;
  undefined8 local_10e0;
  undefined4 local_10d8;
  undefined1 local_10d4;
  undefined1 local_10d0 [4];
  undefined4 local_10cc;
  undefined4 local_f4c;
  undefined4 local_f2c;
  undefined4 local_f0c;
  undefined4 local_eec;
  undefined4 local_ecc;
  undefined4 local_eac;
  undefined4 local_e8c;
  undefined4 local_e6c;
  undefined4 local_e4c;
  undefined4 local_e2c;
  undefined4 local_e0c;
  undefined4 local_dec;
  undefined4 local_dcc;
  undefined4 local_da4;
  undefined4 local_d6c;
  undefined4 local_d5c;
  undefined4 local_d58;
  undefined4 local_d1c;
  undefined4 local_a3c;
  undefined4 local_a38;
  undefined4 local_9fc;
  undefined4 local_71c;
  undefined4 local_718;
  undefined4 local_6dc;
  undefined1 local_408 [964];
  undefined4 local_44;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar18 = (ulong)(param_1 & 0xffff) * 0x2af0;
  lVar10 = *(long *)(DAT_0273ea80 + 8);
  uVar7 = *(undefined4 *)(lVar10 + 0x738 + lVar18);
  puVar16 = param_2;
  puVar17 = (undefined8 *)(lVar10 + 0x760 + lVar18);
  for (lVar15 = 0xf; lVar15 != 0; lVar15 = lVar15 + -1) {
    *puVar17 = *puVar16;
    puVar16 = puVar16 + 1;
    puVar17 = puVar17 + 1;
  }
  *(undefined4 *)(lVar10 + 0x7d8 + lVar18) = *(undefined4 *)(param_2 + 0xf);
  *(undefined2 *)(lVar10 + 0x7dc + lVar18) = *(undefined2 *)((long)param_2 + 0x7c);
  *(undefined2 *)(lVar10 + 0x7de + lVar18) = *(undefined2 *)((long)param_2 + 0x7e);
  *(undefined2 *)(lVar10 + 0x7e0 + lVar18) = *(undefined2 *)(param_2 + 0x10);
  *(undefined2 *)(lVar10 + 0x7e2 + lVar18) = *(undefined2 *)((long)param_2 + 0x82);
  *(undefined1 *)(lVar10 + 0x7e4 + lVar18) = *(undefined1 *)((long)param_2 + 0x84);
  *(undefined4 *)(lVar10 + 0x7e8 + lVar18) = *(undefined4 *)(param_2 + 0x11);
  *(undefined8 *)(lVar10 + 0x810 + lVar18) = param_2[0x16];
  *(undefined8 *)(lVar10 + 0x808 + lVar18) = param_2[0x15];
  *(undefined8 *)(lVar10 + 0x800 + lVar18) = param_2[0x14];
  uVar11 = param_2[0x12];
  *(undefined8 *)(lVar10 + 0x7f8 + lVar18) = param_2[0x13];
  *(undefined8 *)(lVar10 + 0x7f0 + lVar18) = uVar11;
  cVar13 = *(char *)((long)param_2 + 0x5a);
  local_10d4 = *(undefined1 *)((long)param_2 + 0x77);
  local_10d8 = *(undefined4 *)((long)param_2 + 0x73);
  local_10e0 = *(undefined8 *)((long)param_2 + 0x6b);
  local_10f0 = *(undefined8 *)((long)param_2 + 0x5b);
  local_10e8 = *(undefined8 *)((long)param_2 + 99);
  iVar8 = *(int *)(param_2 + 0x12);
  uVar9 = *(undefined4 *)(param_2 + 0x11);
  uVar2 = *(undefined1 *)((long)param_2 + 0x84);
  uVar3 = *(undefined2 *)((long)param_2 + 0x82);
  uVar1 = *(undefined4 *)(param_2 + 0xf);
  uVar4 = *(undefined2 *)(param_2 + 0x10);
  uVar5 = *(undefined2 *)((long)param_2 + 0x7e);
  uVar6 = *(undefined2 *)((long)param_2 + 0x7c);
  local_1118 = *(undefined8 *)((long)param_2 + 0x94);
  local_1110 = *(undefined8 *)((long)param_2 + 0x9c);
  local_10f8 = *(undefined4 *)((long)param_2 + 0xb4);
  local_1100 = *(undefined8 *)((long)param_2 + 0xac);
  local_1108 = *(undefined8 *)((long)param_2 + 0xa4);
  thunk_FUN_012aaab6(lVar10 + 0x6a8 + lVar18,param_2,0x5a);
  *(char *)(lVar10 + 0x702 + lVar18) = cVar13;
  *(undefined1 *)(lVar10 + 0x71f + lVar18) = local_10d4;
  *(undefined4 *)(lVar10 + 0x71b + lVar18) = local_10d8;
  *(undefined8 *)(lVar10 + 0x713 + lVar18) = local_10e0;
  *(undefined8 *)(lVar10 + 0x70b + lVar18) = local_10e8;
  *(undefined8 *)(lVar10 + 0x703 + lVar18) = local_10f0;
  *(undefined4 *)(lVar10 + 0x720 + lVar18) = uVar1;
  *(undefined2 *)(lVar10 + 0x724 + lVar18) = uVar6;
  *(undefined2 *)(lVar10 + 0x726 + lVar18) = uVar5;
  *(undefined2 *)(lVar10 + 0x728 + lVar18) = uVar4;
  *(undefined2 *)(lVar10 + 0x72a + lVar18) = uVar3;
  *(undefined1 *)(lVar10 + 0x72c + lVar18) = uVar2;
  *(undefined4 *)(lVar10 + 0x730 + lVar18) = uVar9;
  *(int *)(lVar10 + 0x738 + lVar18) = iVar8;
  *(undefined4 *)(lVar10 + 0x75c + lVar18) = local_10f8;
  *(undefined8 *)(lVar10 + 0x754 + lVar18) = local_1100;
  *(undefined8 *)(lVar10 + 0x74c + lVar18) = local_1108;
  *(undefined8 *)(lVar10 + 0x744 + lVar18) = local_1110;
  *(undefined8 *)(lVar10 + 0x73c + lVar18) = local_1118;
  if ((((*(char *)(DAT_0273ea90 + 0xa8) != '\0') &&
       (local_1120 = *(long *)(DAT_0273ea90 + 0xa9),
       *(long *)(*(long *)(DAT_0273ea80 + 8) + 0x620 + lVar18) == local_1120)) &&
      (cVar12 = (char)((uint)iVar8 >> 8), (char)((uint)uVar7 >> 8) != cVar12)) &&
     (cVar13 == (char)((uint)iVar8 >> 0x18))) {
    iVar19 = (iVar8 >> 0x18) + 0x10;
    if (iVar8 >> 0x18 == -1) {
      iVar19 = -1;
    }
    uVar7 = *(undefined4 *)(lVar10 + 4 + lVar18);
    if (cVar12 == '\x01') {
      if (param_3 == '\0') {
        local_1130[0] = DAT_0265216c;
        FUN_00911760(local_1130,uVar7,iVar19);
      }
    }
    else if (cVar12 == '\x02') {
      iVar14 = FUN_009236f0(param_1);
      if (param_3 == '\0') {
        local_1128[0] = DAT_02652170;
        FUN_00911760(local_1128,uVar7,iVar19);
      }
      if (iVar14 != -1) {
        FUN_00b28cd0(iVar14,(int)(char)iVar8);
      }
    }
  }
  local_10cc = 0x811c9dc5;
  local_f4c = 0x811c9dc5;
  local_f2c = 0x811c9dc5;
  local_f0c = 0x811c9dc5;
  local_eec = 0x811c9dc5;
  local_ecc = 0x811c9dc5;
  local_eac = 0x811c9dc5;
  local_e8c = 0x811c9dc5;
  local_e6c = 0x811c9dc5;
  local_e4c = 0x811c9dc5;
  local_e2c = 0x811c9dc5;
  local_e0c = 0x811c9dc5;
  local_dec = 0x811c9dc5;
  local_dcc = 0x811c9dc5;
  local_da4 = 0x811c9dc5;
  local_d6c = 0x811c9dc5;
  local_d5c = 0x811c9dc5;
  local_d58 = 0x811c9dc5;
  local_d1c = 0x811c9dc5;
  local_a3c = 0x811c9dc5;
  local_a38 = 0x811c9dc5;
  local_9fc = 0x811c9dc5;
  local_71c = 0x811c9dc5;
  local_718 = 0x811c9dc5;
  local_6dc = 0x811c9dc5;
  FUN_01042f20(local_408);
  local_44 = 0x811c9dc5;
  cVar13 = FUN_00912240(param_1,local_10d0);
  if (cVar13 != '\0') {
    FUN_0073dac0(param_1,local_10d0);
    *(undefined1 *)(*(long *)(DAT_0273ea80 + 8) + 0x2840 + lVar18) = 1;
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

