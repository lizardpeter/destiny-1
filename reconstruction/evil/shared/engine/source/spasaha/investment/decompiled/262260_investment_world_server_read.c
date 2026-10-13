
undefined8
FUN_00262260(undefined8 param_1,undefined4 param_2,int param_3,short *param_4,int param_5,
            int *param_6)

{
  long lVar1;
  char cVar2;
  undefined1 uVar3;
  short sVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  int iVar8;
  long lVar9;
  long *plVar10;
  ulong uVar11;
  undefined8 uVar12;
  long lVar13;
  ushort uVar14;
  long lVar15;
  long lVar16;
  byte bVar17;
  byte bVar18;
  uint uVar19;
  byte bVar20;
  bool bVar21;
  byte local_255;
  undefined1 local_250 [20];
  undefined4 local_23c;
  undefined8 local_230;
  undefined8 local_228;
  undefined8 local_220;
  undefined8 local_218;
  int local_210;
  undefined8 auStack_208 [17];
  undefined1 local_180;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_23c = 1;
  FUN_00072240(local_250,param_1,param_2);
  local_180 = 0;
  FUN_00072400(local_250);
  lVar9 = (long)local_210;
  auStack_208[lVar9 * 4 + 3] = local_218;
  auStack_208[lVar9 * 4 + 2] = local_220;
  auStack_208[lVar9 * 4 + 1] = local_228;
  auStack_208[lVar9 * 4] = local_230;
  local_210 = local_210 + 1;
  *param_6 = 0;
  if (param_5 < 0x20) {
    cVar2 = FUN_000e4d70(7,4);
    bVar17 = 0;
    bVar18 = 0;
    local_255 = 0;
    bVar20 = 0;
    if (cVar2 == '\0') goto LAB_00262a79;
    if ((DAT_02652b00 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_02652b00), iVar5 != 0)) {
      DAT_02652af8 = FUN_000e4a10(s_networking_investment_server_mes_01620e77);
      thunk_FUN_012aa7e6(&DAT_02652b00);
    }
    FUN_01008290(local_178,s_networking_investment_server_mes_01620e77);
    uVar6 = DAT_02652af8;
  }
  else {
    *param_6 = 0x20;
    param_4[0xc] = 0;
    param_4[0xd] = 0;
    param_4[0xe] = 0;
    param_4[0xf] = 0;
    param_4[8] = 0;
    param_4[9] = 0;
    param_4[10] = 0;
    param_4[0xb] = 0;
    param_4[4] = 0;
    param_4[5] = 0;
    param_4[6] = 0;
    param_4[7] = 0;
    param_4[0] = 0;
    param_4[1] = 0;
    param_4[2] = 0;
    param_4[3] = 0;
    uVar6 = FUN_00072c70(local_250,0x10);
    sVar4 = FUN_002800e0(uVar6);
    *param_4 = sVar4;
    if (sVar4 == -1) {
      cVar2 = FUN_000e4d70(7,4);
      bVar17 = 0;
      bVar18 = 0;
      local_255 = 0;
      bVar20 = 0;
      if (cVar2 == '\0') goto LAB_00262a79;
      if ((DAT_02652b10 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_02652b10), iVar5 != 0)) {
        DAT_02652b08 = FUN_000e4a10(s_networking_investment_server_mes_01620ee2);
        thunk_FUN_012aa7e6(&DAT_02652b10);
      }
      FUN_01008290(local_178,s_networking_investment_server_mes_01620ee2,(int)*param_4);
      uVar6 = DAT_02652b08;
    }
    else {
      plVar10 = (long *)FUN_0025cbd0();
      lVar9 = (**(code **)(*plVar10 + 0x4d0))(plVar10,*param_4);
      if (lVar9 != 0) {
        if (param_3 == 1) {
          uVar7 = *(uint *)(lVar9 + 0x18);
        }
        else {
          uVar7 = 0xffffffff;
          if (param_3 == 0) {
            uVar7 = *(uint *)(lVar9 + 0x14);
          }
        }
        lVar15 = (ulong)(((uint)((int)uVar7 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar7 >> 0xd) * 0x40;
        lVar13 = *DAT_01a238a0;
        lVar16 = (long)*param_6 + (long)param_4;
        lVar1 = *(long *)(lVar13 + 0x10 + lVar15);
        uVar11 = (ulong)((uVar7 & 0x1fff) * *(int *)(lVar13 + 0x30 + lVar15));
        bVar17 = *(byte *)(((lVar1 + uVar11) -
                           ((long)*(int *)(lVar13 + 0x34 + lVar15) & *(ulong *)(lVar1 + 8 + uVar11))
                           ) + 0x18);
        iVar5 = (int)lVar16;
        iVar5 = (-(uint)bVar17 & (bVar17 - 1) + iVar5) - iVar5;
        if (param_5 < iVar5 + *param_6) {
          cVar2 = FUN_000e4d70(7,4);
          local_255 = 0;
          if (cVar2 != '\0') {
            if ((DAT_02652b30 == '\0') && (iVar8 = thunk_FUN_012aa7d6(&DAT_02652b30), iVar8 != 0)) {
              DAT_02652b28 = FUN_000e4a10(s_networking_investment_server_mes_01620f9e);
              thunk_FUN_012aa7e6(&DAT_02652b30);
            }
            local_255 = 0;
            FUN_01008290(local_178,s_networking_investment_server_mes_01620f9e,*param_6 + iVar5,
                         param_5);
            FUN_000e4aa0(DAT_02652b28,local_178);
          }
        }
        else {
          local_255 = 1;
          if (0 < iVar5) {
            thunk_FUN_012aa986(lVar16,0,(long)iVar5);
            *param_6 = *param_6 + iVar5;
          }
        }
        if (param_3 == 1) {
          uVar7 = *(uint *)(lVar9 + 0x18);
        }
        else {
          uVar7 = 0xffffffff;
          if (param_3 == 0) {
            uVar7 = *(uint *)(lVar9 + 0x14);
          }
        }
        lVar13 = (ulong)(((uint)((int)uVar7 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar7 >> 0xd) * 0x40;
        lVar9 = *DAT_01a238a0;
        lVar16 = *(long *)(lVar9 + 0x10 + lVar13);
        uVar11 = (ulong)(*(int *)(lVar9 + 0x30 + lVar13) * (uVar7 & 0x1fff));
        iVar5 = *(int *)(((lVar16 + uVar11) -
                         ((long)*(int *)(lVar9 + 0x34 + lVar13) & *(ulong *)(lVar16 + 8 + uVar11)))
                        + 0x14);
        if (param_5 < *param_6 + iVar5) {
          cVar2 = FUN_000e4d70(7,4);
          bVar17 = 0;
          if (cVar2 != '\0') {
            if ((DAT_02652b40 == '\0') && (iVar8 = thunk_FUN_012aa7d6(&DAT_02652b40), iVar8 != 0)) {
              DAT_02652b38 = FUN_000e4a10(s_networking_investment_server_mes_01621039);
              thunk_FUN_012aa7e6(&DAT_02652b40);
            }
            FUN_01008290(local_178,s_networking_investment_server_mes_01621039,iVar5 + *param_6,
                         param_5);
            uVar6 = DAT_02652b38;
LAB_00262964:
            bVar17 = 0;
            FUN_000e4aa0(uVar6,local_178);
          }
        }
        else {
          *(long *)(param_4 + 4) = (long)*param_6 + (long)param_4;
          *param_6 = *param_6 + iVar5;
          lVar9 = *DAT_01a238a0;
          uVar11 = (ulong)((uVar7 & 0x1fff) * *(int *)(lVar9 + lVar13 + 0x30));
          lVar16 = *(long *)(lVar9 + lVar13 + 0x10);
          lVar16 = (lVar16 + uVar11) -
                   ((long)*(int *)(lVar9 + lVar13 + 0x34) & *(ulong *)(lVar16 + 8 + uVar11));
          lVar9 = *(long *)(param_4 + 4);
          uVar12 = FUN_000e8680(lVar16,0,0xffffffff);
          thunk_FUN_012aa986(lVar9,0,uVar12);
          uVar14 = *(ushort *)(lVar16 + 0x1c) & 0x78;
          bVar21 = uVar14 != 0;
          if (uVar14 == 0) {
            uVar19 = *(uint *)(lVar16 + 0x20);
            if ((*(ushort *)(lVar16 + 0x1c) & 0x40) != 0) {
              if ((lVar9 == 0) || (lVar13 = FUN_000e8a90(lVar16,lVar9), lVar13 == 0)) {
                uVar19 = uVar19 | 0x5488bf;
              }
              else {
                uVar19 = uVar19 | *(uint *)(lVar13 + 0x20) & 0x5488bf;
              }
            }
            bVar21 = (uVar19 & 0xc08070) != 0;
          }
          if (bVar21) {
            FUN_000e6730(lVar16,lVar9,0,0xffffffff,0);
          }
          cVar2 = FUN_002c9a90(uVar7,local_250,lVar9,lVar9,1);
          if (cVar2 == '\0') {
            cVar2 = FUN_000e4d70(7,4);
            bVar17 = 0;
            if (cVar2 != '\0') {
              if ((DAT_02652b70 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_02652b70), iVar5 != 0))
              {
                DAT_02652b68 = FUN_000e4a10(s_networking_investment_server_mes_016211ae);
                thunk_FUN_012aa7e6(&DAT_02652b70);
              }
              FUN_01008290(local_178,s_networking_investment_server_mes_016211ae);
              uVar6 = DAT_02652b68;
              goto LAB_00262964;
            }
          }
          else {
            cVar2 = FUN_00072210(local_250);
            bVar17 = 1;
            if (cVar2 != '\0') {
              cVar2 = FUN_000e4d70(7,4);
              bVar17 = 0;
              if (cVar2 != '\0') {
                if ((DAT_02652b80 == '\0') &&
                   (iVar5 = thunk_FUN_012aa7d6(&DAT_02652b80), iVar5 != 0)) {
                  DAT_02652b78 = FUN_000e4a10(s_networking_investment_server_mes_01621206);
                  thunk_FUN_012aa7e6(&DAT_02652b80);
                }
                FUN_01008290(local_178,s_networking_investment_server_mes_01621206);
                uVar6 = DAT_02652b78;
                goto LAB_00262964;
              }
            }
          }
        }
        cVar2 = FUN_00073430(local_250);
        if (cVar2 == '\0') {
          param_4[8] = 0;
          param_4[9] = 0;
          param_4[10] = 0;
          param_4[0xb] = 0;
          param_4[0xc] = 0;
          param_4[0xd] = 0;
LAB_00262a6d:
          bVar20 = 1;
        }
        else {
          iVar5 = FUN_00072c70(local_250,0x10);
          *(int *)(param_4 + 0xc) = iVar5;
          if (*param_6 + iVar5 <= param_5) {
            *(long *)(param_4 + 8) = (long)*param_6 + (long)param_4;
            *param_6 = *param_6 + iVar5;
            FUN_000730b0(local_250,*(undefined8 *)(param_4 + 8),*(int *)(param_4 + 0xc) << 3);
            goto LAB_00262a6d;
          }
          cVar2 = FUN_000e4d70(7,4);
          bVar20 = 0;
          if (cVar2 != '\0') {
            if ((DAT_02652b50 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_02652b50), iVar5 != 0)) {
              DAT_02652b48 = FUN_000e4a10(s_networking_investment_server_mes_016210c2);
              thunk_FUN_012aa7e6(&DAT_02652b50);
            }
            bVar20 = 0;
            FUN_01008290(local_178,s_networking_investment_server_mes_016210c2,
                         *(int *)(param_4 + 0xc) + *param_6,param_5);
            FUN_000e4aa0(DAT_02652b48,local_178);
          }
        }
        bVar18 = 1;
        goto LAB_00262a79;
      }
      cVar2 = FUN_000e4d70(7,4);
      bVar17 = 0;
      bVar18 = 0;
      local_255 = 0;
      bVar20 = 0;
      if (cVar2 == '\0') goto LAB_00262a79;
      if ((DAT_02652b20 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_02652b20), iVar5 != 0)) {
        DAT_02652b18 = FUN_000e4a10(s_networking_investment_server_mes_01620f31);
        thunk_FUN_012aa7e6(&DAT_02652b20);
      }
      FUN_01008290(local_178,s_networking_investment_server_mes_01620f31,(int)*param_4);
      uVar6 = DAT_02652b18;
    }
  }
  bVar17 = 0;
  FUN_000e4aa0(uVar6,local_178);
  bVar18 = 0;
  local_255 = 0;
  bVar20 = 0;
LAB_00262a79:
  cVar2 = FUN_00072210(local_250);
  if (cVar2 == '\0') {
    bVar20 = bVar20 & bVar17 & local_255 & bVar18;
  }
  else {
    cVar2 = FUN_000e4d70(7,4);
    bVar20 = 0;
    if (cVar2 != '\0') {
      if ((DAT_02652b60 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_02652b60), iVar5 != 0)) {
        DAT_02652b58 = FUN_000e4a10(s_networking_investment_server_mes_01621153);
        thunk_FUN_012aa7e6(&DAT_02652b60);
      }
      bVar20 = 0;
      FUN_01008290(local_178,s_networking_investment_server_mes_01621153);
      FUN_000e4aa0(DAT_02652b58,local_178);
    }
  }
  uVar3 = FUN_00072210(local_250);
  FUN_00072350(local_250,uVar3);
  FUN_00072650(local_250);
  if (*DAT_01a1f100 != local_38) {
    uVar12 = thunk_FUN_012aa7f6();
    return uVar12;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),bVar20);
}

