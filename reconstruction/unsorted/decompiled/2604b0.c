
void FUN_002604b0(long *param_1,long param_2,undefined1 *param_3)

{
  undefined1 *puVar1;
  undefined1 *puVar2;
  long lVar3;
  code *pcVar4;
  byte bVar5;
  bool bVar6;
  undefined1 uVar7;
  char cVar8;
  long *plVar9;
  undefined8 *puVar10;
  undefined8 uVar11;
  undefined8 uVar12;
  long lVar13;
  undefined8 uVar14;
  long lVar15;
  long lVar16;
  int iVar17;
  bool bVar18;
  bool bVar19;
  undefined1 *puVar20;
  undefined1 auStack_12180 [16];
  byte bStack_12170;
  char cStack_1216f;
  undefined1 uStack_12161;
  undefined1 auStack_12160 [24576];
  undefined1 local_c160 [24576];
  undefined1 local_6160 [24576];
  undefined8 local_160;
  undefined8 uStack_158;
  undefined8 uStack_150;
  undefined8 uStack_148;
  undefined8 local_140;
  undefined8 uStack_138;
  undefined8 uStack_130;
  undefined8 uStack_128;
  undefined8 local_120;
  undefined8 uStack_118;
  undefined8 uStack_110;
  undefined8 uStack_108;
  undefined8 local_100;
  undefined8 uStack_f8;
  undefined8 uStack_f0;
  undefined8 uStack_e8;
  undefined8 local_e0;
  undefined8 uStack_d8;
  undefined8 uStack_d0;
  undefined8 uStack_c8;
  undefined8 local_c0;
  undefined8 uStack_b8;
  undefined8 uStack_b0;
  undefined8 uStack_a8;
  undefined8 local_a0;
  undefined8 uStack_98;
  undefined8 uStack_90;
  undefined8 uStack_88;
  undefined8 local_80;
  undefined8 uStack_78;
  undefined8 uStack_70;
  undefined8 uStack_68;
  long local_60;
  
  local_60 = *DAT_01a1f100;
  uStack_12161 = 1;
  plVar9 = (long *)FUN_0025a550();
  puVar10 = (undefined8 *)(**(code **)(*param_1 + 0x30))(param_1);
  uVar11 = (**(code **)(*param_1 + 0x18))(param_1);
  uVar12 = (**(code **)(*param_1 + 8))(param_1);
  lVar13 = (**(code **)(*param_1 + 0x10))(param_1);
  puVar2 = param_3 + 0x4804;
  local_80 = 0;
  uStack_78 = 0;
  uStack_70 = 0;
  uStack_68 = 0;
  local_a0 = 0;
  uStack_98 = 0;
  uStack_90 = 0;
  uStack_88 = 0;
  local_c0 = 0;
  uStack_b8 = 0;
  uStack_b0 = 0;
  uStack_a8 = 0;
  local_e0 = 0;
  uStack_d8 = 0;
  uStack_d0 = 0;
  uStack_c8 = 0;
  local_100 = 0;
  uStack_f8 = 0;
  uStack_f0 = 0;
  uStack_e8 = 0;
  local_120 = 0;
  uStack_118 = 0;
  uStack_110 = 0;
  uStack_108 = 0;
  local_140 = 0;
  uStack_138 = 0;
  uStack_130 = 0;
  uStack_128 = 0;
  local_160 = 0;
  uStack_158 = 0;
  uStack_150 = 0;
  uStack_148 = 0;
  *(undefined4 *)(param_3 + 0x4804) = 0;
  if (lVar13 == 0) {
    uStack_12161 = 0;
  }
  else {
    FUN_00275ca0(param_1,param_3 + 0x4004);
  }
  puVar20 = param_3 + 0x4004;
  puVar1 = param_3 + 4;
  FUN_0028c830(puVar1);
  FUN_0028c4d0(param_1,puVar20,puVar2,puVar1,puVar1);
  FUN_00275df0(puVar1,&local_160,3,puVar20);
  uVar14 = (**(code **)(*param_1 + 0x20))(param_1);
  uVar7 = (**(code **)(*param_1 + 0x58))();
  cVar8 = FUN_0028de90(puVar10,uVar11,uVar12,lVar13,puVar20,puVar2,puVar1,uVar14,param_2,uVar7,
                       local_6160,local_c160,auStack_12160);
  if (cVar8 == '\0') {
    uStack_12161 = 0;
  }
  FUN_0028e0c0(local_6160,local_c160,auStack_12160,puVar1);
  if ((puVar10 == (undefined8 *)0x0) || (lVar13 == 0)) {
    uStack_12161 = 0;
  }
  else {
    lVar3 = lVar13 + 0x2b80;
    FUN_00269230(auStack_12180);
    do {
      FUN_002692a0(auStack_12180);
      if (cStack_1216f == '\0') break;
      bVar6 = false;
      bVar18 = false;
      if (param_2 == 0) {
        do {
          iVar17 = (int)(char)bStack_12170;
          bVar5 = bStack_12170 & 0x1f;
          if ((*(uint *)(param_3 + (long)(iVar17 >> 5) * 4 + 0x4804) >> (bStack_12170 & 0x1f) & 1)
              == 0) {
            pcVar4 = *(code **)*puVar10;
            uVar11 = FUN_00269370(auStack_12180);
            lVar15 = (*pcVar4)(puVar10,uVar11);
            if ((lVar15 == 0) ||
               (lVar16 = (**(code **)(*plVar9 + 0x410))(plVar9,*(undefined2 *)(lVar15 + 0x24)),
               lVar16 == 0)) {
              uStack_12161 = 0;
            }
            else {
              cVar8 = FUN_00269a50(puVar1,puVar20,lVar3,puVar10,lVar15,0);
              if (cVar8 != '\0') {
                *(uint *)(param_3 + (long)(iVar17 >> 5) * 4 + 0x4804) =
                     *(uint *)(param_3 + (long)(iVar17 >> 5) * 4 + 0x4804) | 1 << bVar5;
                cVar8 = FUN_0028d730(lVar16,lVar15,puVar1,local_c160,&uStack_12161);
                bVar6 = true;
                bVar19 = true;
                if (cVar8 == '\0') {
                  bVar19 = bVar18;
                }
                bVar18 = bVar19;
                if (*(short *)(lVar15 + 0x58) != -1) {
                  FUN_00275b80(lVar15 + 0x38,puVar20);
                }
              }
            }
          }
          FUN_00269300(auStack_12180);
        } while (cStack_1216f != '\0');
      }
      else {
        do {
          iVar17 = (int)(char)bStack_12170;
          bVar5 = bStack_12170 & 0x1f;
          if ((*(uint *)(param_3 + (long)(iVar17 >> 5) * 4 + 0x4804) >> (bStack_12170 & 0x1f) & 1)
              == 0) {
            lVar15 = *(long *)(param_2 + 8);
            if ((((lVar15 == 0) || (*(long *)(lVar15 + 0x18) == 0)) ||
                (lVar16 = *(long *)(lVar15 + 0x18) + lVar15 + 0x18, lVar16 == 0)) ||
               (bStack_12170 != *(byte *)(lVar16 + 0x18))) {
              pcVar4 = *(code **)*puVar10;
              uVar11 = FUN_00269370(auStack_12180);
              lVar16 = (*pcVar4)(puVar10,uVar11);
              if (lVar16 != 0) {
                lVar15 = (**(code **)(*plVar9 + 0x410))(plVar9,*(undefined2 *)(lVar16 + 0x24));
                bVar19 = false;
                goto LAB_00260a34;
              }
            }
            else {
              lVar16 = *(long *)(param_2 + 0x10);
              bVar19 = true;
LAB_00260a34:
              if ((lVar15 != 0) && (lVar16 != 0)) {
                if ((bVar19) ||
                   (cVar8 = FUN_00269a50(puVar1,puVar20,lVar3,puVar10,lVar16,0), cVar8 != '\0')) {
                  *(uint *)(param_3 + (long)(iVar17 >> 5) * 4 + 0x4804) =
                       *(uint *)(param_3 + (long)(iVar17 >> 5) * 4 + 0x4804) | 1 << bVar5;
                  cVar8 = FUN_0028d730(lVar15,lVar16,puVar1,local_c160,&uStack_12161);
                  bVar6 = true;
                  bVar19 = true;
                  if (cVar8 == '\0') {
                    bVar19 = bVar18;
                  }
                  bVar18 = bVar19;
                  if (*(short *)(lVar16 + 0x58) != -1) {
                    FUN_00275b80(lVar16 + 0x38,puVar20);
                  }
                }
                goto LAB_00260a58;
              }
            }
            uStack_12161 = 0;
          }
LAB_00260a58:
          FUN_00269300(auStack_12180);
        } while (cStack_1216f != '\0');
      }
      if (bVar18) {
        FUN_0028e0c0(local_6160,local_c160,auStack_12160,puVar1);
      }
    } while (bVar6);
    uVar7 = FUN_000014d0();
    FUN_00281e70(lVar13 + 8,lVar3,puVar2,puVar10,puVar1,uVar7,lVar13 + 0x6fd0,&local_160);
    FUN_00275df0(puVar1,&local_160,5,puVar20);
    FUN_00275df0(puVar1,&local_160,6,puVar20);
    FUN_00275df0(puVar1,&local_160,3,puVar20);
    FUN_00275df0(puVar1,&local_160,4,puVar20);
  }
  *param_3 = 1;
  param_3[1] = uStack_12161;
  param_3[2] = 0;
  if (*DAT_01a1f100 != local_60) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

