
void FUN_007d8c30(float param_1)

{
  float fVar1;
  undefined8 uVar2;
  undefined1 auVar3 [16];
  int iVar4;
  long lVar5;
  undefined4 uVar6;
  ushort uVar7;
  ulong uVar8;
  uint uVar9;
  float fVar10;
  uint local_48 [2];
  long local_40;
  uint local_38;
  uint uStack_34;
  undefined8 *local_30;
  long local_28;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  uVar2 = *(undefined8 *)(*(long *)(DAT_026df1d0 + 8) + 0x10);
  uVar6 = FUN_0006f140(&DAT_026df1d0);
  FUN_0008f550(local_48,uVar2,uVar6);
  lVar5 = DAT_026df1d0;
  local_30 = &DAT_026df1d0;
  local_28 = DAT_026df1d0;
  uVar8 = (ulong)local_38;
  if ((int)local_48[0] < (int)local_38) {
    do {
      uVar7 = 0xffff;
      if ((int)local_48[0] < (int)uVar8) {
        uVar7 = (ushort)local_48[0];
      }
      uVar9 = 0xffffffff;
      if (uVar7 != 0xffff) {
        if ((DAT_026df204 & 0x40000000) == 0) {
          uVar9 = uVar7 & 0x1fff;
        }
        else {
          uVar9 = uVar7 & 0x1fff;
        }
      }
      uVar8 = (ulong)((uVar9 & 0x1fff) * DAT_026df1e0);
      fVar1 = *(float *)(uVar8 + 0xc + DAT_026df1d8);
      fVar10 = DAT_0165fd54;
      if (DAT_0165fd58 <= fVar1) {
        fVar10 = param_1 / fVar1;
      }
      auVar3 = vminss_avx(ZEXT416((uint)DAT_0165fd54),
                          ZEXT416((uint)(fVar10 + *(float *)(uVar8 + 8 + DAT_026df1d8))));
      *(int *)(uVar8 + 8 + DAT_026df1d8) = auVar3._0_4_;
      uVar8 = CONCAT44(uStack_34,local_38);
      do {
        iVar4 = (int)uVar8;
        uVar8 = uVar8 >> 0x20;
        uVar9 = local_48[0];
        do {
          local_48[0] = uVar9 + 1;
          if (iVar4 <= (int)local_48[0]) break;
          uVar8 = uVar8 >> 1;
          uStack_34 = (uint)uVar8;
          if (uStack_34 == 0) {
            local_48[0] = uVar9 + 0x20 & 0xffffffe0;
            if (iVar4 <= (int)local_48[0]) break;
            uStack_34 = *(uint *)(local_40 + (long)((int)(uVar9 + 0x20) >> 5) * 4);
            while (uVar8 = (ulong)uStack_34, uStack_34 == 0) {
              local_48[0] = local_48[0] + 0x20;
              if (iVar4 <= (int)local_48[0]) goto LAB_007d8e15;
              uStack_34 = *(uint *)(local_40 + (long)((int)local_48[0] >> 5) * 4);
            }
          }
          uVar9 = local_48[0];
        } while ((uVar8 & 1) == 0);
LAB_007d8e15:
        uVar8 = CONCAT44(uStack_34,local_38);
        if ((int)local_38 <= (int)local_48[0]) goto LAB_007d8e41;
      } while ((*(uint *)(*(long *)(*(long *)(lVar5 + 8) + 0x10) +
                         (ulong)(local_48[0] >> 5 & 0x7ff) * 4) >> (local_48[0] & 0x1f) & 1) == 0);
    } while( true );
  }
LAB_007d8e41:
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

