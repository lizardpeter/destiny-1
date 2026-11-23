
undefined8 FUN_00644ed0(uint *param_1,long param_2)

{
  long lVar1;
  long lVar2;
  ulong uVar3;
  float fVar4;
  bool bVar5;
  undefined1 uVar6;
  char cVar7;
  uint uVar8;
  int iVar9;
  ulong uVar10;
  undefined8 uVar11;
  long lVar12;
  uint uVar13;
  ulong uVar14;
  undefined1 local_68 [48];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar13 = param_1[0xb];
  uVar8 = 1 << ((byte)uVar13 & 0x1f) & *(uint *)(&DAT_0267fe58 + (ulong)(uVar13 >> 5 & 0xff) * 4);
  uVar6 = false;
  if ((*(byte *)((ulong)((uVar13 & 0x1fff) * DAT_02692230) + 4 + DAT_02692228) & 4) != 0)
  goto switchD_00644f59_default;
  switch((char)param_1[0xaa]) {
  case '\x02':
    uVar6 = 0;
    if (uVar8 != 0) {
      param_1[0x6d] = (uint)(*(float *)(param_2 + 4) + (float)param_1[0x6d]);
      iVar9 = FUN_00071f60(param_1 + 0x28);
      if (iVar9 == -1) {
        FUN_00644e20(param_1);
        uVar6 = 1;
      }
      else {
        uVar6 = 1;
        if ((float)param_1[0x6c] <= (float)param_1[0x6d]) {
          param_1[0x6c] = 0xff7fffff;
          param_1[0x6d] = 0xff7fffff;
          FUN_00645230(param_1);
        }
      }
    }
    break;
  case '\x03':
    uVar6 = 0;
    if (uVar8 != 0) {
      param_1[0x6d] = (uint)(*(float *)(param_2 + 4) + (float)param_1[0x6d]);
      iVar9 = FUN_00071f60(param_1 + 0x28);
      if ((iVar9 != -1) && (iVar9 = FUN_00071f60(param_1 + 0x42), iVar9 != -1)) {
        bVar5 = false;
        if ((0.0 <= (float)param_1[0x6c]) && ((float)param_1[0x6c] < (float)param_1[0x6d])) {
          bVar5 = true;
        }
        iVar9 = FUN_00071f60(param_1 + 0x48);
        lVar1 = DAT_026897f8;
        if (iVar9 != -1) {
          uVar10 = (ulong)((param_1[0x49] & 0x1fff) * DAT_02689800);
          uVar14 = (ulong)DAT_02689818;
          uVar3 = *(ulong *)(DAT_026897f8 + 8 + uVar10);
          FUN_0100f280(local_68,param_1 + 0x3c);
          FUN_00355460(local_68);
          cVar7 = FUN_005bbbf0((lVar1 + uVar10) - (uVar14 & uVar3));
          if ((!bVar5) && (uVar6 = 1, cVar7 != '\x01')) break;
        }
      }
      FUN_00645760(param_1);
      uVar6 = 1;
    }
    break;
  case '\x04':
    uVar6 = 0;
    if (uVar8 == 0) break;
    fVar4 = *(float *)(param_2 + 4) + (float)param_1[0x6d];
    param_1[0x6d] = (uint)fVar4;
    uVar6 = 1;
    bVar5 = true;
    if (fVar4 < (float)param_1[0x6c]) break;
    goto LAB_0064519a;
  case '\x05':
  case '\x06':
  case '\a':
  case '\b':
    uVar6 = FUN_006459d0(param_1);
    break;
  case '\t':
    uVar6 = uVar8 != 0;
  default:
switchD_00644f59_default:
    if (uVar8 != 0) {
LAB_00645172:
      if (((param_1[0x20] != param_1[0x21]) || (param_1[0x21] != 0xffffffff)) &&
         (iVar9 = FUN_00071f60(param_1 + 0x20), bVar5 = (bool)uVar6, iVar9 == -1)) {
LAB_0064519a:
        uVar6 = bVar5;
        FUN_00644e20(param_1);
      }
    }
    break;
  case '\n':
    uVar6 = 0;
    if (uVar8 == 0) break;
    uVar13 = (int)*param_1 >> 0xd;
    fVar4 = *(float *)(param_2 + 4) + (float)param_1[0xab];
    lVar12 = (ulong)((uVar13 >> 0x12 | 0x3ff) & uVar13) * 0x40;
    lVar1 = *DAT_01a238a0;
    uVar6 = true;
    lVar2 = *(long *)(lVar1 + 0x10 + lVar12);
    iVar9 = *(int *)(lVar1 + 0x34 + lVar12);
    uVar10 = (ulong)((*param_1 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar12));
    uVar3 = *(ulong *)(lVar2 + 8 + uVar10);
    param_1[0xab] = (uint)fVar4;
    if (*(float *)(*(long *)(param_1 + 2) + 0x22c + ((lVar2 + uVar10) - ((long)iVar9 & uVar3))) <=
        fVar4) {
      FUN_00644e20(param_1);
    }
    goto LAB_00645172;
  }
  *(undefined1 *)(param_1 + 0xac) = uVar6;
  if (*DAT_01a1f100 != local_38) {
    uVar11 = thunk_FUN_012aa7f6();
    return uVar11;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar6);
}

