
undefined8 FUN_007dab10(void)

{
  ulong *puVar1;
  int *piVar2;
  int iVar3;
  int *piVar4;
  byte bVar5;
  int iVar6;
  int *piVar7;
  ulong uVar8;
  undefined8 uVar9;
  ulong uVar10;
  ulong uVar11;
  int *piVar12;
  int *piVar13;
  byte bVar14;
  bool bVar15;
  undefined8 local_58;
  undefined8 local_50;
  undefined1 local_48 [16];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_007db290(local_48);
  piVar4 = DAT_026df268;
  uVar10 = *(ulong *)(DAT_026df268 + 0xa000);
  bVar14 = 1;
  if ((((int)(uVar10 >> 0x20) != (int)uVar10) && (DAT_026df268[(uVar10 & 0xffffffff) * 0x10] == 1))
     && (DAT_026df268 + (uVar10 & 0xffffffff) * 0x10 != (int *)0x0)) {
    puVar1 = (ulong *)(DAT_026df268 + 0xa000);
    piVar2 = DAT_026df268 + 0x9ff0;
    piVar12 = DAT_026df268 + (uVar10 & 0xffffffff) * 0x10;
    do {
      bVar14 = 0;
      if (((char)piVar12[0xf] != '\x01') || (bVar5 = FUN_007db2c0(local_48,piVar12), bVar5 == 0))
      break;
      if (*(code **)(piVar12 + 8) != (code *)0x0) {
        local_50 = *(undefined8 *)(piVar12 + 10);
        local_58 = *(undefined8 *)(piVar12 + 0xc);
        (**(code **)(piVar12 + 8))
                  (&local_50,&local_58,*(undefined8 *)(piVar12 + 2),*(undefined8 *)(piVar12 + 4));
      }
      FUN_007db2b0(piVar12);
      piVar7 = piVar12 + 0x10;
      if (piVar2 == piVar12) {
        piVar7 = piVar4;
      }
      uVar10 = *(ulong *)(piVar4 + 0xa000);
      if ((uint)(uVar10 >> 0x20) < (uint)uVar10) {
        if ((long)piVar7 - (long)(piVar4 + (uVar10 & 0xffffffff) * 0x10) < 0) {
LAB_007dac3e:
          piVar13 = (int *)0x0;
          if (-1 < (long)piVar7 - (long)(piVar4 + (uVar10 >> 0x20) * 0x10)) goto LAB_007dac52;
        }
        piVar13 = (int *)0x0;
        if (*piVar7 == 1) {
          piVar13 = piVar7;
        }
      }
      else {
        piVar13 = (int *)0x0;
        if (-1 < (long)piVar7 - (long)(piVar4 + (uVar10 & 0xffffffff) * 0x10)) goto LAB_007dac3e;
      }
LAB_007dac52:
      uVar10 = *puVar1;
      do {
        iVar3 = *piVar12;
        LOCK();
        iVar6 = *piVar12;
        if (iVar3 == iVar6) {
          *piVar12 = 0;
          iVar6 = iVar3;
        }
        UNLOCK();
      } while (iVar3 != iVar6);
      uVar11 = (ulong)((int)uVar10 + 1);
      if ((int)uVar10 == 0x9ff) {
        uVar11 = 0;
      }
      do {
        LOCK();
        uVar8 = *puVar1;
        if (uVar10 == uVar8) {
          *puVar1 = uVar10 & 0xffffffff00000000 | uVar11;
          uVar8 = uVar10;
        }
        UNLOCK();
        bVar15 = uVar8 != uVar10;
        uVar10 = uVar8;
      } while (bVar15);
      piVar12 = piVar13;
      bVar14 = bVar5;
    } while ((piVar13 != (int *)0x0 & bVar5) == 1);
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),bVar14);
  }
  uVar9 = thunk_FUN_012aa7f6();
  return uVar9;
}

