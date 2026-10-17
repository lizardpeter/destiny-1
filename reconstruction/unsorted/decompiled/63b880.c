
void FUN_0063b880(char *param_1)

{
  char *pcVar1;
  int *piVar2;
  undefined8 uVar3;
  long lVar4;
  undefined4 uVar5;
  ulong uVar6;
  uint uVar7;
  uint uVar8;
  uint local_60 [2];
  long local_58;
  int local_50;
  uint uStack_4c;
  char *local_48;
  long *local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if ((param_1[1] != '\0') || (*param_1 != '\0')) {
    param_1[0] = '\0';
    param_1[1] = '\0';
    uVar3 = *(undefined8 *)(*(long *)(*(long *)(param_1 + 0x10) + 8) + 0x10);
    pcVar1 = param_1 + 0x10;
    uVar5 = FUN_0006f140(pcVar1);
    FUN_0008f550(local_60,uVar3,uVar5);
    local_40 = *(long **)(param_1 + 0x10);
    local_48 = pcVar1;
    if ((int)local_60[0] < local_50) {
      do {
        uVar6 = (ulong)((local_60[0] & 0xffff) * (int)local_40[2]);
        lVar4 = *local_40;
        piVar2 = (int *)(lVar4 + uVar6);
        if (*(char *)(lVar4 + 0x10c + uVar6) == '\0') {
          if ((1 < *piVar2 - 6U) && (FUN_00639d30(piVar2), 1 < *piVar2 - 6U)) {
            param_1[1] = '\x01';
          }
        }
        else {
          FUN_00639d30(piVar2);
          if (((*piVar2 == 8) && (*(short *)(uVar6 + 0x128 + lVar4) == 0)) &&
             (*(short *)(uVar6 + 0x12a + lVar4) == 0)) {
            FUN_0058bf90(piVar2);
            uVar6 = (ulong)local_60[0];
            if (local_50 <= (int)local_60[0]) {
              uVar6 = 0xffff;
            }
            uVar8 = 0xffffffff;
            if ((short)uVar6 != -1) {
              uVar7 = *(uint *)(*(long *)(local_48 + 8) +
                               (ulong)*(uint *)(local_48 + 0x1c) +
                               (ulong)*(uint *)(local_48 + 0x20) * (uVar6 & 0xffff)) &
                      *(uint *)(local_48 + 0x24);
              uVar8 = *(uint *)(local_48 + 0x34);
              if ((uVar8 & 0x40000000) == 0) {
                uVar8 = (uVar7 & 0xff) << 0x17 | (uVar8 & 0x3ff) << 0xd | (uint)uVar6 & 0x1fff;
              }
              else {
                uVar8 = (uVar7 & 7) << 0x1b | (uVar8 & 0x3fff) << 0xd | (uint)uVar6 & 0x1fff |
                        0x80000000;
              }
            }
            FUN_0006ecb0(pcVar1,uVar8);
          }
          else {
            *param_1 = '\x01';
          }
        }
        uVar6 = (ulong)uStack_4c;
LAB_0063ba20:
        do {
          uVar8 = local_60[0] + 1;
          if ((int)uVar8 < local_50) {
            uVar6 = uVar6 >> 1;
            uStack_4c = (uint)uVar6;
            if (uStack_4c == 0) {
              uVar8 = local_60[0] + 0x20;
              local_60[0] = uVar8 & 0xffffffe0;
              if (local_50 <= (int)local_60[0]) {
LAB_0063ba8e:
                uVar6 = 0;
                uVar8 = local_60[0];
                goto LAB_0063ba90;
              }
              uStack_4c = *(uint *)(local_58 + (long)((int)uVar8 >> 5) * 4);
              while (uVar6 = (ulong)uStack_4c, uVar8 = local_60[0], uStack_4c == 0) {
                local_60[0] = local_60[0] + 0x20;
                if (local_50 <= (int)local_60[0]) goto LAB_0063ba8e;
                uStack_4c = *(uint *)(local_58 + (long)((int)local_60[0] >> 5) * 4);
              }
            }
            local_60[0] = uVar8;
            uVar8 = local_60[0];
            if ((uVar6 & 1) == 0) goto LAB_0063ba20;
          }
LAB_0063ba90:
          local_60[0] = uVar8;
          if (local_50 <= (int)local_60[0]) goto LAB_0063bae4;
        } while ((*(uint *)(*(long *)(local_40[1] + 0x10) + (ulong)(local_60[0] >> 5 & 0x7ff) * 4)
                  >> (local_60[0] & 0x1f) & 1) == 0);
      } while( true );
    }
  }
LAB_0063bae4:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

