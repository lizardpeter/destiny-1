
undefined8 FUN_00f69070(long param_1,int param_2,long param_3,undefined4 param_4)

{
  byte bVar1;
  undefined1 uVar2;
  undefined *puVar3;
  int iVar4;
  undefined8 uVar5;
  int iVar6;
  undefined *puVar7;
  long lVar8;
  undefined *puVar9;
  undefined1 local_48 [16];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (param_1 == 0) {
    FUN_00f6c180(s_gcm____NULL_016c2280,s_C__bungie_external_libraries_lib_016c2385,0x28);
  }
  if (param_3 == 0) {
    FUN_00f6c180(s_key____NULL_016c21b4,s_C__bungie_external_libraries_lib_016c2385,0x29);
  }
  uVar5 = FUN_00f6c1a0(param_2);
  if ((int)uVar5 == 0) {
    uVar5 = 10;
    if (*(int *)(PTR_DAT_01a1fff8 + (long)param_2 * 0xb0 + 0x14) == 0x10) {
      uVar5 = (**(code **)(PTR_DAT_01a1fff8 + (long)param_2 * 0xb0 + 0x20))
                        (param_3,param_4,0,param_1);
      if ((int)uVar5 == 0) {
        FUN_00f6c140(param_1 + 0x10e0,0x10);
        FUN_00f6c140(param_1 + 0x10b0,0x10);
        *(int *)(param_1 + 0x10f0) = param_2;
        *(undefined4 *)(param_1 + 0x110c) = 0;
        *(undefined8 *)(param_1 + 0x1104) = 0;
        *(undefined8 *)(param_1 + 0x10fc) = 0;
        *(undefined8 *)(param_1 + 0x10f4) = 0;
        FUN_00f6c140(local_48,0x10);
        uVar5 = FUN_00f693a0(param_1,local_48,param_1 + 0x10a0);
        if ((int)uVar5 == 0) {
          FUN_00f6c140(local_48,0x10);
          lVar8 = param_1 + 0x1110;
          iVar6 = 0;
          do {
            local_48[0] = (undefined1)iVar6;
            FUN_00f6ff60(param_1 + 0x10a0,local_48,lVar8);
            puVar3 = PTR_DAT_01a20000;
            lVar8 = lVar8 + 0x10;
            iVar6 = iVar6 + 1;
          } while (iVar6 != 0x100);
          puVar9 = &DAT_0000211f + param_1;
          iVar6 = 1;
          do {
            iVar4 = 0x100;
            puVar7 = puVar9;
            do {
              bVar1 = puVar7[-0x1000];
              *puVar7 = puVar7[-0x1001];
              puVar7[-1] = puVar7[-0x1002];
              puVar7[-2] = puVar7[-0x1003];
              uVar2 = puVar3[(uint)bVar1 * 2];
              puVar7[-3] = puVar7[-0x1004];
              puVar7[-4] = puVar7[-0x1005];
              puVar7[-5] = puVar7[-0x1006];
              puVar7[-6] = puVar7[-0x1007];
              puVar7[-7] = puVar7[-0x1008];
              puVar7[-8] = puVar7[-0x1009];
              puVar7[-9] = puVar7[-0x100a];
              puVar7[-10] = puVar7[-0x100b];
              puVar7[-0xb] = puVar7[-0x100c];
              puVar7[-0xc] = puVar7[-0x100d];
              puVar7[-0xd] = puVar7[-0x100e];
              bVar1 = puVar3[bVar1 + 1 + (uint)bVar1];
              iVar4 = iVar4 + -1;
              puVar7[-0xf] = uVar2;
              puVar7[-0xe] = puVar7[-0x100f] ^ bVar1;
              puVar7 = puVar7 + 0x10;
            } while (iVar4 != 0);
            puVar9 = puVar9 + 0x1000;
            iVar6 = iVar6 + 1;
            uVar5 = 0;
          } while (iVar6 != 0x10);
        }
      }
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return uVar5;
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

