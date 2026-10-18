
undefined8 FUN_00ba3770(undefined8 *param_1,int param_2,char param_3)

{
  char cVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  long lVar5;
  undefined8 uVar6;
  long lVar7;
  long lVar8;
  undefined1 local_180;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar5 = FUN_0075f130(*param_1);
  local_180 = 0;
  if (((lVar5 != 0) && (*(uint *)(lVar5 + 0x8c48) < 0xb)) &&
     ((0x3f0U >> (*(uint *)(lVar5 + 0x8c48) & 0x1f) & 1) != 0)) {
    uVar6 = FUN_00b74340(lVar5);
    iVar2 = FUN_00b81650(uVar6,(long)param_1 + (long)param_2 * 8 + 0x2c);
    iVar3 = FUN_00b743b0(lVar5,iVar2);
    if (iVar3 != -1) {
      cVar1 = FUN_00b743f0(lVar5,iVar3);
      if (cVar1 != '\0') {
        cVar1 = FUN_00af8b70(param_1[2],*(undefined4 *)(lVar5 + 0x610),iVar3);
        if (cVar1 != '\0') {
          lVar7 = FUN_00af8d60(param_1[2],*(undefined4 *)(lVar5 + 0x610),iVar3);
          if (iVar2 != -1) {
            lVar8 = FUN_00b74340(lVar5);
            if (*(int *)(lVar7 + 0x1ca8) == 5) {
              lVar7 = lVar8 + 0x30 + (long)iVar2 * 0x168;
              lVar8 = FUN_00ba2680(param_1[1],param_2);
              if (lVar8 == 0) {
                uVar6 = FUN_00b74340(lVar5);
                uVar6 = FUN_00b81740(uVar6,iVar2);
                lVar5 = FUN_00b74340(lVar5);
                uVar4 = thunk_FUN_012aa826(lVar7,lVar5 + 0x30 +
                                                 (long)*(int *)(lVar5 + 0x5d0c) * 0x168,0x24);
                FUN_00ba23c0(param_1[1],uVar6,param_2,s__unknown_view_016973ff + 1,uVar4 >> 0x1f);
                lVar8 = FUN_00ba26d0(param_1[1],uVar6);
                if (lVar8 == 0) {
                  cVar1 = FUN_000e4d70(0x10,4);
                  local_180 = 0;
                  if (cVar1 != '\0') {
                    if (DAT_028a5cd8 == '\0') {
                      iVar2 = thunk_FUN_012aa7d6(&DAT_028a5cd8);
                      if (iVar2 != 0) {
                        DAT_028a5cd0 = FUN_000e4a10(s_networking_simulation_domain_mem_0169740d);
                        thunk_FUN_012aa7e6(&DAT_028a5cd8);
                      }
                    }
                    local_180 = 0;
                    FUN_01008290(local_178,s_networking_simulation_domain_mem_0169740d,param_2);
                    FUN_000e4aa0(DAT_028a5cd0,local_178);
                  }
                  goto LAB_00ba3a48;
                }
              }
              if (*(long *)(lVar8 + 0x68) == 0) {
                lVar5 = FUN_00058050(param_1[1]);
                FUN_00bb31d0(lVar8,lVar5 + 0x2898 + (long)iVar3 * 0x6c8,lVar7);
                *(undefined4 *)(lVar8 + 0x80) = *(undefined4 *)(param_1 + 0x1a);
              }
              cVar1 = FUN_00bb3e90(lVar8);
              if (param_3 == '\0') {
                local_180 = 1;
                if (cVar1 != '\0') {
                  FUN_00ba2490(param_1[1],lVar8);
                  local_180 = 0;
                }
              }
              else {
                local_180 = 1;
                if (cVar1 == '\0') {
                  FUN_00bb3ea0(lVar8);
                }
              }
            }
          }
        }
      }
    }
  }
LAB_00ba3a48:
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),local_180);
  }
  uVar6 = thunk_FUN_012aa7f6();
  return uVar6;
}

