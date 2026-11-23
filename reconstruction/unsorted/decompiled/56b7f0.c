
void FUN_0056b7f0(long param_1)

{
  char *pcVar1;
  long lVar2;
  char *pcVar3;
  char cVar4;
  long lVar5;
  long lVar6;
  long lVar7;
  long lVar8;
  undefined8 *puVar9;
  uint uVar10;
  ulong uVar11;
  long lVar12;
  
  lVar6 = 0;
  do {
    lVar8 = lVar6 * 0x40;
    lVar5 = param_1 + 0x8c + lVar8;
    FUN_00544000(lVar5);
    lVar2 = param_1 + 0x94 + lVar8;
    FUN_00544000(lVar2);
    cVar4 = FUN_0010b400(lVar2);
    pcVar1 = (char *)(param_1 + 0x60 + lVar8);
    if (cVar4 == '\0') {
      pcVar3 = (char *)(param_1 + 0x88 + lVar8);
      cVar4 = *(char *)(param_1 + 0x88 + lVar8);
      if (cVar4 == '\x04') {
        cVar4 = FUN_0010b400(lVar5);
        if (cVar4 == '\0') {
          cVar4 = *pcVar3;
        }
        else {
          FUN_00543ee0(lVar5);
          *pcVar3 = '\x01';
          cVar4 = '\x01';
        }
      }
      if ((int)cVar4 - 2U < 2) {
        if (((*pcVar1 == '\x02') && (*(char *)(param_1 + 0x8a + lVar8) == '\0')) &&
           ((*(char *)(param_1 + 0x8b + lVar8) == '\0' &&
            (lVar5 = FUN_0034e490(), *(char *)(lVar5 + 0x28) == '\0')))) {
          FUN_00552b10((int)*pcVar1,param_1 + 0x80 + lVar8);
          *pcVar3 = '\x01';
          lVar5 = 0;
          do {
            lVar2 = param_1 + lVar8;
            if (0 < *(short *)(lVar2 + 100 + lVar5 * 4)) {
              lVar7 = (long)*pcVar1 * 0x60 + param_1;
              lVar12 = (long)*(int *)(lVar5 * 0x10 + 0x4fd98 + lVar7);
              uVar11 = (ulong)*(uint *)(lVar5 * 0x10 + 0x4fd90 + lVar7);
              lVar7 = 0;
              if (uVar11 != 0xffffffff) {
                lVar7 = uVar11 + param_1 + 0x40a0;
              }
              uVar11 = (ulong)*(short *)(lVar2 + 0x62 + lVar5 * 4);
              puVar9 = (undefined8 *)(uVar11 * lVar12 + lVar7);
              do {
                thunk_FUN_012aa986(puVar9,0,lVar12);
                *puVar9 = 0;
                puVar9 = (undefined8 *)((long)puVar9 + lVar12);
                uVar10 = (int)uVar11 + 1;
                uVar11 = (ulong)uVar10;
              } while ((int)uVar10 <
                       (int)*(short *)(lVar2 + 100 + lVar5 * 4) +
                       (int)*(short *)(lVar2 + 0x62 + lVar5 * 4));
            }
            lVar5 = lVar5 + 1;
          } while ((int)lVar5 != 6);
        }
      }
      else if (cVar4 == 1) {
        cVar4 = *pcVar1;
        if (((cVar4 == '\x02') && (cVar4 = '\x02', *(char *)(param_1 + 0x8a + lVar8) == '\0')) &&
           (*(char *)(param_1 + 0x8b + lVar8) == '\0')) {
          lVar5 = FUN_0034e490();
          if (*(char *)(lVar5 + 0x28) == '\0') goto LAB_0056ba40;
          cVar4 = *pcVar1;
        }
        FUN_00552a60((int)cVar4,param_1 + 0x80 + lVar8);
        lVar5 = FUN_0034e490();
        if (*(char *)(lVar5 + 0x4d) != '\0') {
          lVar5 = FUN_0034e490();
          FUN_00543f70(lVar2,*(undefined4 *)(lVar5 + 0x50));
        }
        *pcVar3 = '\x02';
      }
    }
    else {
      FUN_0056ba70(param_1,(int)*pcVar1,param_1 + 0x80 + lVar8,0);
    }
LAB_0056ba40:
    lVar6 = lVar6 + 1;
    if ((int)lVar6 == 0x101) {
      return;
    }
  } while( true );
}

