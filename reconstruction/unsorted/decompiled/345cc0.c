
ulong FUN_00345cc0(byte param_1,code *param_2,undefined8 param_3,long *param_4,undefined4 param_5,
                  int *param_6)

{
  long *plVar1;
  long *plVar2;
  uint uVar3;
  char cVar4;
  byte bVar5;
  int iVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  long lVar10;
  long lVar11;
  long lVar12;
  byte bVar13;
  int iVar14;
  long local_1070;
  undefined4 local_1058 [2];
  undefined4 local_1050 [2];
  undefined4 local_1048 [2];
  int local_1040;
  undefined4 local_103c [1025];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar10 = *param_4;
  iVar14 = (int)lVar10;
  if (param_1 == 0) {
    *param_6 = iVar14;
    bVar5 = 1;
    if (iVar14 < 1) goto LAB_00346033;
    thunk_FUN_012aa986(param_6 + 1,0xff,(lVar10 * 4 + 0x3fffffffcU & 0x3fffffffc) + 4);
  }
  bVar5 = 1;
  if (0 < iVar14) {
    bVar5 = 1;
    local_1070 = 0;
    do {
      if ((bVar5 & 1) == 0) break;
      uVar3 = *(uint *)((long)(param_4 + 1) + local_1070 * 4 + param_4[1] + 0x10);
      if (uVar3 == 0xffffffff) {
        (*param_2)(5,0,s_client_blueprint_set_is_missing__0162b443);
        bVar5 = 0;
      }
      else {
        lVar8 = (ulong)(((uint)((int)uVar3 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar3 >> 0xd) * 0x40;
        lVar10 = *DAT_01a238a0;
        lVar12 = *(long *)(lVar10 + 0x10 + lVar8);
        uVar7 = (ulong)((uVar3 & 0x1fff) * *(int *)(lVar10 + 0x30 + lVar8));
        lVar10 = (lVar12 + uVar7) -
                 ((long)*(int *)(lVar10 + 0x34 + lVar8) & *(ulong *)(lVar12 + 8 + uVar7));
        bVar13 = bVar5;
        if (param_1 == 0) {
          iVar6 = FUN_00106d60(lVar10,param_5);
          bVar13 = 0;
          if (iVar6 == 0) {
            local_1048[0] = *(undefined4 *)(lVar10 + 0xc);
            cVar4 = FUN_002d6500(local_1048,lVar10 + 0x10);
            if (cVar4 == '\0') {
              (*param_2)(6,0,s_failed_to_register_client_bundle_0162b4e1);
            }
            else {
              local_1050[0] = *(undefined4 *)(lVar10 + 0xc);
              iVar6 = FUN_001d87e0(local_1050,1);
              if (iVar6 == -1) {
                (*param_2)(6,0,s_failed_to_instantiate_client_bun_0162b4bd);
              }
              else {
                param_6[local_1070 + 1] = iVar6;
                bVar13 = bVar5;
              }
            }
          }
        }
        bVar5 = bVar13;
        if (0 < *(long *)(lVar10 + 0x30)) {
          plVar1 = (long *)(lVar10 + 0x38);
          lVar12 = 0;
          do {
            if ((bVar5 & 1) == 0) break;
            lVar8 = *plVar1;
            if ((byte)(*(uint *)((long)plVar1 + lVar12 * 0x28 + lVar8 + 0x10) < 0x80 | param_1 ^ 1)
                == 1) {
              local_1040 = 0;
              FUN_00107890((long)plVar1 + lVar12 * 0x28 + lVar8 + 0x18);
              local_1040 = 0;
              if (0 < *(long *)((long)plVar1 + lVar12 * 0x28 + lVar8 + 0x28)) {
                plVar2 = (long *)((long)plVar1 + lVar12 * 0x28 + lVar8 + 0x30);
                lVar9 = 0;
                do {
                  if (*(int *)((long)plVar2 + lVar9 * 4 + *plVar2 + 0x10) == -1) {
                    (*param_2)(6,0,s_sensor_classes_are_invalid___imp_0162b417);
                    bVar5 = 0;
                    goto LAB_00345ff0;
                  }
                  lVar11 = (long)local_1040;
                  local_1040 = local_1040 + 1;
                  local_103c[lVar11] = *(undefined4 *)((long)plVar2 + lVar9 * 4 + *plVar2 + 0x10);
                  lVar9 = lVar9 + 1;
                } while (lVar9 < *(long *)((long)plVar1 + lVar12 * 0x28 + lVar8 + 0x28));
              }
              local_1058[0] = *(undefined4 *)(lVar10 + 0xc);
              bVar5 = FUN_001d8120(local_1058,1,local_1040,local_103c);
              if (bVar5 == 0) {
                (*param_2)(6,0,s_failed_to_add_to_global_client_b_0162b3f1);
                bVar5 = 0;
              }
            }
LAB_00345ff0:
            lVar12 = lVar12 + 1;
          } while (lVar12 < *(long *)(lVar10 + 0x30));
        }
      }
      local_1070 = local_1070 + 1;
    } while ((int)local_1070 < iVar14);
  }
LAB_00346033:
  if (*DAT_01a1f100 != local_38) {
    uVar7 = thunk_FUN_012aa7f6();
    return uVar7;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),bVar5) & 0xffffffffffffff01;
}

