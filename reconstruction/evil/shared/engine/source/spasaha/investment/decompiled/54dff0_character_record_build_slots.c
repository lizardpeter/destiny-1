
undefined1
FUN_0054dff0(undefined8 *param_1,undefined8 *param_2,undefined1 *param_3,undefined8 param_4,
            long param_5,undefined2 *param_6,long param_7,undefined8 *param_8)

{
  short sVar1;
  undefined2 uVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  int iVar5;
  undefined8 uVar6;
  long *plVar7;
  int *piVar8;
  undefined4 *puVar9;
  undefined8 uVar10;
  long lVar11;
  long lVar12;
  long lVar13;
  long lVar14;
  undefined1 *puVar15;
  uint uVar16;
  int iVar17;
  char *pcVar18;
  long lVar19;
  ushort uVar20;
  undefined8 extraout_RDX;
  char *pcVar21;
  char cVar22;
  undefined1 uVar23;
  undefined8 *puVar24;
  bool bVar25;
  undefined1 auVar26 [16];
  char *local_e0;
  undefined1 local_b8 [16];
  undefined4 local_a8 [2];
  long local_a0;
  char local_98 [8];
  long local_90;
  char local_88 [8];
  long local_80;
  undefined8 local_78;
  undefined8 local_70;
  undefined8 local_68;
  undefined8 local_60;
  undefined8 local_58;
  undefined8 local_50;
  undefined8 local_48;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  param_8[1] = 0;
  *param_8 = 0;
  *param_8 = *param_1;
  param_8[1] = *param_2;
  uVar6 = FUN_005494c0();
  FUN_0054a010(uVar6);
  plVar7 = (long *)FUN_0025cbd0();
  piVar8 = (int *)(**(code **)(*plVar7 + 0x100))(plVar7);
  FUN_0054dd80(param_8 + 2);
  *(undefined1 *)(param_8 + 2) = param_3[2];
  *(undefined1 *)((long)param_8 + 0x11) = param_3[1];
  *(undefined1 *)((long)param_8 + 0x12) = *param_3;
  auVar26 = FUN_0054a0f0(uVar6,param_3[2]);
  if ((auVar26._0_8_ == 0) || (auVar26._8_8_ == 0)) {
    *(undefined4 *)((long)param_8 + 0x1c) = 0xffffffff;
  }
  else {
    puVar9 = (undefined4 *)FUN_0054c7b0(uVar6,*(undefined2 *)(auVar26._8_8_ + 4));
    uVar10 = FUN_0033fa20();
    local_a8[0] = *puVar9;
    uVar4 = FUN_0033fc20(uVar10,local_a8);
    *(undefined4 *)((long)param_8 + 0x1c) = uVar4;
  }
  FUN_0054ed90(param_3,param_4,uVar6,extraout_RDX,param_8 + 2);
  thunk_FUN_012aa7c6(param_8 + 0x83,param_5,0xa08);
  plVar7 = (long *)FUN_0025cbd0();
  lVar11 = (**(code **)(*plVar7 + 0x160))(plVar7);
  local_80 = param_5 + 0x908;
  local_90 = param_5 + 0x988;
  local_a0 = param_5 + 0x888;
  local_a8[0] = CONCAT31(local_a8[0]._1_3_,*(undefined1 *)(lVar11 + 0x11));
  local_98[0] = *(char *)(lVar11 + 0x13);
  local_88[0] = *(char *)(lVar11 + 0x12);
  if (DAT_0295d2e1 == '\0') {
    lVar11 = *(long *)(PTR_DAT_0197e2a8 + 8);
    uVar10 = FUN_000e8680(lVar11,0,0xffffffff);
    thunk_FUN_012aa986(&local_58,0,uVar10);
    uVar20 = *(ushort *)(lVar11 + 0x1c) & 0x78;
    bVar25 = uVar20 != 0;
    if (uVar20 == 0) {
      uVar16 = *(uint *)(lVar11 + 0x20);
      if ((*(ushort *)(lVar11 + 0x1c) & 0x40) != 0) {
        lVar12 = FUN_000e8a90(lVar11,&local_58);
        if (lVar12 == 0) {
          uVar16 = uVar16 | 0x5488bf;
        }
        else {
          uVar16 = *(uint *)(lVar12 + 0x20) & 0x5488bf | uVar16;
        }
      }
      bVar25 = (uVar16 & 0xc08070) != 0;
    }
    if (bVar25) {
      FUN_000e6730(lVar11,&local_58,0,0xffffffff,0);
    }
    DAT_0295d2d0 = local_40;
    DAT_0295d2c8 = local_48;
    DAT_0295d2c0 = local_50;
    DAT_0295d2b8 = local_58;
    DAT_0295d2e1 = '\x01';
  }
  local_60 = DAT_0295d2d0;
  local_68 = DAT_0295d2c8;
  local_70 = DAT_0295d2c0;
  local_78 = DAT_0295d2b8;
  iVar5 = (int)*(undefined8 *)piVar8;
  if (0 < iVar5) {
    cVar22 = '\x01';
    if (param_7 == 0) {
      puVar24 = param_8;
      do {
        sVar1 = *(short *)(param_5 + 0x1f0 + (long)(char)(cVar22 + -1) * 0x40);
        puVar24 = (undefined8 *)CONCAT62((int6)((ulong)puVar24 >> 0x10),sVar1);
        if (sVar1 != -1) {
          plVar7 = (long *)FUN_0025cbd0();
          lVar11 = (**(code **)(*plVar7 + 0x410))(plVar7,(ulong)puVar24 & 0xffffffff);
          if (((lVar11 != 0) && (*(long *)(lVar11 + 0x60) != 0)) &&
             (lVar11 = *(long *)(lVar11 + 0x60) + lVar11 + 0x60, lVar11 != 0)) {
            FUN_0028a280(lVar11 + 0x50,1,&local_78);
          }
        }
        iVar17 = (int)cVar22;
        cVar22 = cVar22 + '\x01';
        iVar5 = (int)*(undefined8 *)piVar8;
      } while (iVar17 < iVar5);
    }
    else {
      do {
        sVar1 = *(short *)(param_5 + 0x1f0 + (long)(char)(cVar22 + -1) * 0x40);
        lVar11 = *(long *)(param_7 + 8);
        if ((((lVar11 == 0) || (*(long *)(lVar11 + 0x18) == 0)) ||
            ((lVar12 = *(long *)(lVar11 + 0x18) + lVar11 + 0x18, lVar12 == 0 ||
             (((char)(cVar22 + -1) != *(char *)(lVar12 + 0x18) || (*(long *)(lVar11 + 0x60) == 0))))
            )) || (lVar11 = *(long *)(lVar11 + 0x60) + lVar11 + 0x60, lVar11 == 0)) {
          if (sVar1 != -1) {
            plVar7 = (long *)FUN_0025cbd0();
            lVar11 = (**(code **)(*plVar7 + 0x410))(plVar7,sVar1);
            if (((lVar11 != 0) && (*(long *)(lVar11 + 0x60) != 0)) &&
               (lVar11 = *(long *)(lVar11 + 0x60) + lVar11 + 0x60, lVar11 != 0)) goto LAB_0054e322;
          }
        }
        else {
LAB_0054e322:
          FUN_0028a280(lVar11 + 0x50,1,&local_78);
        }
        iVar17 = (int)cVar22;
        cVar22 = cVar22 + '\x01';
        iVar5 = (int)*(undefined8 *)piVar8;
      } while (iVar17 < iVar5);
    }
  }
  uVar3 = 1;
  if (0 < iVar5) {
    cVar22 = '\0';
    uVar23 = 1;
    do {
      lVar11 = (long)cVar22;
      lVar12 = lVar11 * 0x40;
      uVar2 = *(undefined2 *)(param_5 + 500 + lVar12);
      param_8[lVar11 * 4 + 0x34] = 0xffffffffffffffff;
      param_8[lVar11 * 4 + 0x33] = 0xffffffffffffffff;
      param_8[lVar11 * 4 + 0x32] = 0xffffffffffffffff;
      param_8[lVar11 * 4 + 0x31] = 0xffffffffffffffff;
      pcVar18 = (char *)local_a8;
      if (cVar22 != (char)local_a8[0]) {
        pcVar18 = (char *)0x0;
      }
      pcVar21 = local_98;
      if (cVar22 != local_98[0]) {
        pcVar21 = pcVar18;
      }
      local_e0 = local_88;
      if (cVar22 != local_88[0]) {
        local_e0 = pcVar21;
      }
      if (((param_7 == 0) || (lVar13 = *(long *)(param_7 + 8), lVar13 == 0)) ||
         ((*(long *)(lVar13 + 0x18) == 0 ||
          ((lVar19 = *(long *)(lVar13 + 0x18) + lVar13 + 0x18, lVar19 == 0 ||
           (bVar25 = true, cVar22 != *(char *)(lVar19 + 0x18))))))) {
        uVar3 = uVar23;
        if (*(short *)(param_5 + 0x1f0 + lVar12) != -1) {
          plVar7 = (long *)FUN_0025cbd0();
          lVar13 = (**(code **)(*plVar7 + 0x410))(plVar7,*(undefined2 *)(param_5 + 0x1f0 + lVar12));
          bVar25 = false;
          uVar3 = 0;
          if (lVar13 != 0) goto LAB_0054e521;
        }
      }
      else {
LAB_0054e521:
        uVar3 = uVar23;
        if ((*(long *)(lVar13 + 0x60) != 0) &&
           (lVar19 = *(long *)(lVar13 + 0x60) + lVar13 + 0x60, lVar19 != 0)) {
          if (bVar25) {
            uVar4 = FUN_0028a330(lVar19,param_3[2]);
            lVar14 = FUN_0054c5b0(uVar6,uVar4);
            puVar15 = (undefined1 *)(param_5 + 0x1f6 + lVar12);
            if ((param_7 != 0) && (*(long *)(param_7 + 0x10) != 0)) {
              FUN_0028a380(*(long *)(param_7 + 0x10) + 0x26,param_3,local_b8);
              FUN_00289d40(0,lVar13,*(undefined8 *)(param_7 + 0x10),&local_78,
                           param_8 + lVar11 * 8 + 0xc5);
              puVar15 = local_b8;
            }
          }
          else {
            lVar14 = FUN_0054c5b0(uVar6,CONCAT62((int6)((ulong)param_5 >> 0x10),uVar2) & 0xffffffff)
            ;
            puVar15 = (undefined1 *)(param_5 + 0x1f6 + lVar12);
          }
          if (lVar14 != 0) {
            uVar10 = 0;
            if (local_e0 != (char *)0x0) {
              uVar10 = *(undefined8 *)(local_e0 + 8);
            }
            FUN_0054f840(uVar6,param_3[1],lVar14,*(undefined2 *)(lVar19 + 0x60),
                         local_e0 != (char *)0x0,uVar10,puVar15,param_8 + lVar11 * 4 + 0x31);
          }
        }
      }
      cVar22 = cVar22 + '\x01';
      uVar23 = uVar3;
    } while ((int)cVar22 < *piVar8);
  }
  if (param_6 == (undefined2 *)0x0) {
    *(undefined2 *)((long)param_8 + 0x184) = 0xffff;
  }
  else {
    *(undefined2 *)((long)param_8 + 0x184) = *param_6;
  }
  if (*DAT_01a1f100 == local_38) {
    return uVar3;
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

