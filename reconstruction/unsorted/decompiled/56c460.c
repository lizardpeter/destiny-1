
void FUN_0056c460(long param_1,char *param_2,long param_3,int param_4)

{
  char cVar1;
  uint uVar2;
  long lVar3;
  long *plVar4;
  ulong uVar5;
  short sVar6;
  long lVar7;
  ulong uVar8;
  long lVar9;
  long lVar10;
  int iVar11;
  long lVar12;
  short sVar13;
  long lVar14;
  int iVar15;
  undefined8 *puVar16;
  undefined8 local_7610;
  undefined1 local_7608 [30160];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_7610 = *(undefined8 *)(param_2 + 0x20);
  uVar5 = 0;
  do {
    sVar13 = *(short *)(param_2 + uVar5 * 4 + 4);
    if (0 < sVar13) {
      lVar7 = (long)*param_2 * 0x60 + param_1;
      lVar9 = uVar5 * 0x10;
      lVar14 = (long)*(int *)(lVar9 + 0x4fd98 + lVar7);
      uVar2 = *(uint *)(lVar9 + 0x4fd9c + lVar7);
      uVar8 = (ulong)*(uint *)(lVar9 + 0x4fd90 + lVar7);
      lVar7 = 0;
      if (uVar8 != 0xffffffff) {
        lVar7 = uVar8 + param_1 + 0x40a0;
      }
      lVar10 = (ulong)(((uint)((int)uVar2 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar2 >> 0xd) * 0x40;
      lVar9 = *DAT_01a238a0;
      uVar8 = (ulong)((uVar2 & 0x1fff) * *(int *)(lVar9 + 0x30 + lVar10));
      if (0 < sVar13) {
        sVar6 = *(short *)(param_2 + uVar5 * 4 + 2);
        lVar12 = (long)sVar6;
        if (param_4 < 1) {
          iVar15 = (int)sVar6;
          plVar4 = (long *)(lVar7 + lVar12 * lVar14);
          do {
            if (*plVar4 != 0) {
              cVar1 = *param_2;
              thunk_FUN_012aa7c6(local_7608,plVar4,lVar14);
              thunk_FUN_012aa986(plVar4,0,lVar14);
              *plVar4 = 0;
              FUN_0056f940(local_7608,uVar2,(int)cVar1,&local_7610,uVar5 & 0xffffffff);
              sVar13 = *(short *)(param_2 + uVar5 * 4 + 4);
              sVar6 = *(short *)(param_2 + uVar5 * 4 + 2);
            }
            plVar4 = (long *)((long)plVar4 + lVar14);
            iVar15 = iVar15 + 1;
          } while (iVar15 < (int)sVar13 + (int)sVar6);
        }
        else {
          lVar3 = *(long *)(lVar9 + 0x10 + lVar10);
          iVar15 = *(int *)(((lVar3 + uVar8) -
                            ((long)*(int *)(lVar9 + 0x34 + lVar10) & *(ulong *)(lVar3 + 8 + uVar8)))
                           + 8);
          do {
            lVar9 = *(long *)(lVar7 + lVar12 * lVar14);
            if (lVar9 != 0) {
              iVar11 = 0;
              puVar16 = (undefined8 *)(lVar12 * lVar14 + lVar7);
              plVar4 = (long *)(param_3 + 4);
              do {
                if ((*(int *)((long)plVar4 + -4) == iVar15) && (*plVar4 == lVar9))
                goto LAB_0056c667;
                plVar4 = plVar4 + 2;
                iVar11 = iVar11 + 1;
              } while (iVar11 < param_4);
              cVar1 = *param_2;
              thunk_FUN_012aa7c6(local_7608,puVar16,lVar14);
              thunk_FUN_012aa986(puVar16,0,lVar14);
              *puVar16 = 0;
              FUN_0056f940(local_7608,uVar2,(int)cVar1,&local_7610,uVar5 & 0xffffffff);
              sVar13 = *(short *)(param_2 + uVar5 * 4 + 4);
              sVar6 = *(short *)(param_2 + uVar5 * 4 + 2);
            }
LAB_0056c667:
            lVar12 = lVar12 + 1;
          } while ((int)lVar12 < (int)sVar13 + (int)sVar6);
        }
      }
    }
    uVar5 = uVar5 + 1;
    if ((int)uVar5 == 6) {
      if (*DAT_01a1f100 != local_38) {
        thunk_FUN_012aa7f6();
        return;
      }
      return;
    }
  } while( true );
}

