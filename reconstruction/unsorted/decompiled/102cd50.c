
void FUN_0102cd50(undefined4 *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  long lVar1;
  long lVar2;
  long *plVar3;
  char cVar4;
  int iVar5;
  uint uVar6;
  ulong uVar7;
  long lVar8;
  undefined4 uVar9;
  uint local_30 [2];
  long local_28;
  
  plVar3 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  cVar4 = FUN_00073430(param_4);
  if (cVar4 == '\0') {
    FUN_00073430(param_4);
    uVar9 = 0xffffffff;
  }
  else {
    local_30[0] = 0xffffffff;
    FUN_002c7d80(local_30,s_entity_index_016271c7,param_4,1);
    uVar9 = 0xffffffff;
    if (local_30[0] < 0xfffffffe) {
      iVar5 = FUN_002403b0();
      if (iVar5 != -1) {
        uVar6 = FUN_00240370(iVar5);
        if (uVar6 != 0xffffffff) {
          lVar8 = (ulong)(((uint)((int)uVar6 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar6 >> 0xd) * 0x40;
          lVar1 = *DAT_01a238a0;
          lVar2 = *(long *)(lVar1 + 0x10 + lVar8);
          uVar7 = (ulong)((uVar6 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar8));
          uVar9 = *(undefined4 *)
                   (((lVar2 + uVar7) -
                    ((long)*(int *)(lVar1 + 0x34 + lVar8) & *(ulong *)(lVar2 + 8 + uVar7))) + 0xb8);
        }
      }
    }
  }
  *param_1 = uVar9;
  if (*plVar3 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

