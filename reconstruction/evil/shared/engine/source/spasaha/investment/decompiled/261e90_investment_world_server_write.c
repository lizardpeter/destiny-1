
undefined8
FUN_00261e90(undefined2 *param_1,int param_2,undefined8 param_3,undefined4 param_4,int *param_5)

{
  char cVar1;
  int iVar2;
  long *plVar3;
  long lVar4;
  undefined8 uVar5;
  uint uVar6;
  undefined1 uVar7;
  undefined4 uVar8;
  undefined1 local_250 [20];
  undefined4 local_23c;
  int local_230;
  int local_22c;
  ulong local_228;
  uint local_220;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  plVar3 = (long *)FUN_0025cbd0();
  lVar4 = (**(code **)(*plVar3 + 0x4d0))(plVar3,*param_1);
  if (param_2 == 1) {
    uVar8 = *(undefined4 *)(lVar4 + 0x18);
  }
  else {
    uVar8 = 0xffffffff;
    if (param_2 == 0) {
      uVar8 = *(undefined4 *)(lVar4 + 0x14);
    }
  }
  local_23c = 1;
  FUN_00072240(local_250,param_3,param_4);
  *param_5 = 0;
  FUN_000723b0(local_250,1);
  if ((int)(0x40 - local_220) < 0x10) {
    FUN_000733a0(local_250,(ulong)*(ushort *)(lVar4 + 0x10),0x10);
  }
  else {
    local_220 = local_220 + 0x10;
    local_22c = local_22c + 0x10;
    local_228 = local_228 << 0x10 | (ulong)*(ushort *)(lVar4 + 0x10);
  }
  cVar1 = FUN_002c9a80(uVar8,*(undefined8 *)(param_1 + 4),local_250,1);
  if (cVar1 == '\0') {
    cVar1 = FUN_000e4d70(7,4);
    uVar7 = 0;
    if (cVar1 == '\0') goto LAB_0026222a;
    if (DAT_02652b90 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_02652b90);
      if (iVar2 != 0) {
        DAT_02652b88 = FUN_000e4a10(s_networking_investment_server_mes_01621263);
        thunk_FUN_012aa7e6(&DAT_02652b90);
      }
    }
    FUN_01008290(local_178,s_networking_investment_server_mes_01621263);
    uVar8 = DAT_02652b88;
  }
  else {
    cVar1 = FUN_00072210(local_250);
    if (cVar1 == '\0') {
      iVar2 = *(int *)(param_1 + 0xc);
      if (local_220 < 0x40) {
        local_220 = local_220 + 1;
        local_22c = local_22c + 1;
        local_228 = local_228 * 2 | (ulong)(0 < iVar2);
      }
      else {
        FUN_000733a0(local_250,0 < iVar2,1);
      }
      if (0 < iVar2) {
        uVar6 = *(uint *)(param_1 + 0xc);
        if ((int)(0x40 - local_220) < 0x10) {
          FUN_000733a0(local_250,(ulong)uVar6,0x10);
          uVar6 = *(uint *)(param_1 + 0xc);
        }
        else {
          local_220 = local_220 + 0x10;
          local_22c = local_22c + 0x10;
          local_228 = local_228 << 0x10 | (ulong)uVar6;
        }
        FUN_00072e30(local_250,*(undefined8 *)(param_1 + 8),uVar6 << 3,0);
      }
      cVar1 = FUN_00072210(local_250);
      if (cVar1 == '\0') {
        FUN_00072560(local_250,0);
        uVar7 = 1;
        *param_5 = (int)(((uint)((int)(local_230 + 7 + local_220) >> 0x1f) >> 0x1d) + 7 +
                        local_230 + local_220) >> 3;
        goto LAB_0026222a;
      }
      cVar1 = FUN_000e4d70(7,4);
      uVar7 = 0;
      if (cVar1 == '\0') goto LAB_0026222a;
      if (DAT_02652af0 == '\0') {
        iVar2 = thunk_FUN_012aa7d6(&DAT_02652af0);
        if (iVar2 != 0) {
          DAT_02652ae8 = FUN_000e4a10(s_c<333_networking:investment:serv_01620e16 + 6);
          thunk_FUN_012aa7e6(&DAT_02652af0);
        }
      }
      FUN_01008290(local_178,s_c<333_networking:investment:serv_01620e16 + 6);
      uVar8 = DAT_02652ae8;
    }
    else {
      cVar1 = FUN_000e4d70(7,4);
      uVar7 = 0;
      if (cVar1 == '\0') goto LAB_0026222a;
      if (DAT_02652ba0 == '\0') {
        iVar2 = thunk_FUN_012aa7d6(&DAT_02652ba0);
        if (iVar2 != 0) {
          DAT_02652b98 = FUN_000e4a10(s_networking_investment_server_mes_016212c8);
          thunk_FUN_012aa7e6(&DAT_02652ba0);
        }
      }
      FUN_01008290(local_178,s_networking_investment_server_mes_016212c8);
      uVar8 = DAT_02652b98;
    }
  }
  uVar7 = 0;
  FUN_000e4aa0(uVar8,local_178);
LAB_0026222a:
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar7);
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

