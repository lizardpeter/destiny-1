
void FUN_00b2b7a0(long param_1,undefined1 param_2,long param_3)

{
  int iVar1;
  bool bVar2;
  char cVar3;
  ushort uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  undefined4 uVar9;
  long lVar10;
  long lVar11;
  undefined8 uVar12;
  long *plVar13;
  undefined8 local_418;
  char local_410;
  undefined1 local_408 [448];
  undefined4 local_248;
  undefined4 local_244;
  undefined8 local_240;
  undefined8 uStack_238;
  undefined8 uStack_230;
  undefined8 uStack_228;
  undefined8 local_220;
  undefined8 uStack_218;
  undefined8 uStack_210;
  undefined8 uStack_208;
  undefined8 local_200;
  undefined8 uStack_1f8;
  undefined8 uStack_1f0;
  undefined8 uStack_1e8;
  undefined8 local_1e0;
  undefined8 uStack_1d8;
  undefined8 uStack_1d0;
  undefined8 uStack_1c8;
  undefined8 local_1c0;
  undefined8 uStack_1b8;
  undefined8 uStack_1b0;
  undefined8 uStack_1a8;
  undefined8 local_1a0;
  undefined8 uStack_198;
  undefined8 uStack_190;
  undefined8 uStack_188;
  undefined8 local_180;
  undefined8 uStack_178;
  undefined8 uStack_170;
  undefined8 uStack_168;
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
  long local_60;
  
  local_60 = *DAT_01a1f100;
  iVar1 = *(int *)(param_3 + 0x614);
  cVar3 = FUN_00b78180(param_3);
  if (cVar3 == '\0') {
    if ((*(uint *)(param_3 + 0x8c48) < 0xb) &&
       ((0x7f0U >> (*(uint *)(param_3 + 0x8c48) & 0x1f) & 1) != 0)) {
      lVar10 = FUN_00b74340(param_3);
      for (iVar5 = FUN_00b80f40(lVar10); iVar5 != -1; iVar5 = FUN_00b80f70(lVar10,iVar5)) {
        if (*(int *)(lVar10 + 0x5c + (long)iVar5 * 0x168) != 10) goto LAB_00b2bc1b;
      }
    }
    iVar5 = FUN_00b1dc70();
    if (iVar5 < 1) {
      uVar4 = *(ushort *)(param_1 + 0x1f80);
      if ((uVar4 & 5) == 1) {
        FUN_00b100b0(param_1,*(undefined4 *)(param_1 + 0xcd4));
        uVar4 = *(ushort *)(param_1 + 0x1f80) | 4;
        *(ushort *)(param_1 + 0x1f80) = uVar4;
      }
      if ((uVar4 & 4) != 0) {
        FUN_00b10b50(param_1,param_2);
        FUN_00b0fbf0(param_1);
        lVar11 = FUN_00b10a00(param_1);
        lVar10 = DAT_026553b0;
        if (DAT_026553a8 == '\0') {
          lVar10 = FUN_000694d0();
        }
        iVar5 = FUN_00768440();
        if (((long)iVar5 <= lVar10 - lVar11) && ((*(byte *)(param_1 + 0x1f80) & 0x60) == 0)) {
          FUN_00b10490(param_1);
          FUN_00b0fed0(param_1);
        }
        iVar5 = FUN_00b10ac0(param_1);
        cVar3 = FUN_00b10a90(param_1);
        iVar6 = FUN_00b10a70(param_1);
        iVar7 = FUN_00768420();
        iVar8 = FUN_00768430();
        bVar2 = 0 < iVar5;
        if (((0 < iVar5) && (cVar3 == '\x01')) &&
           (bVar2 = (long)iVar8 <= lVar10 - lVar11, iVar7 <= iVar6)) {
          bVar2 = true;
        }
        uVar4 = *(ushort *)(param_1 + 0x1f80);
        if (((uVar4 & 0xe0) == 0) && (bVar2)) {
          uVar4 = uVar4 | 0x10;
        }
        else {
          uVar4 = uVar4 & 0xffef;
        }
        *(ushort *)(param_1 + 0x1f80) = uVar4;
        cVar3 = FUN_00b10a60(param_1);
        uVar4 = *(ushort *)(param_1 + 0x1f80);
        if ((cVar3 != '\0') && ((uVar4 & 8) == 0)) {
          lVar10 = DAT_026553b0;
          if (DAT_026553a8 == '\0') {
            lVar10 = FUN_000694d0();
            uVar4 = *(ushort *)(param_1 + 0x1f80);
          }
          *(long *)((long)&PTR_DAT_00001f78 + param_1) = lVar10;
          uVar4 = uVar4 | 8;
          *(ushort *)(param_1 + 0x1f80) = uVar4;
        }
        if ((uVar4 & 0x10) != 0) {
          cVar3 = FUN_00b10650(param_1,param_1 + 0xcd8);
          if (cVar3 != '\0') {
            uVar12 = thunk_FUN_00768060();
            FUN_00b22190(iVar1);
            if (iVar1 == 2) {
              plVar13 = (long *)FUN_0075d560(0,0);
              lVar10 = FUN_00b0c560(*(undefined4 *)(param_1 + 0xcd0));
              thunk_FUN_012aa986(&local_418,0,0x1d8);
              local_418 = (**(code **)(*plVar13 + 0x10))(plVar13);
              local_410 = (char)*(undefined4 *)(lVar10 + 0x28) + -1;
              if (((*(byte *)(lVar10 + 0x1b9) & 1) == 0) || ((*(byte *)(param_1 + 0x1f80) & 4) == 0)
                 ) {
LAB_00b2bbd1:
                FUN_00b10880(param_1,param_1 + 0xcd8,2);
              }
              else {
                FUN_00b2c490(lVar10,local_408);
                FUN_0076fcf0(uVar12,param_1 + 0x1da8);
                local_248 = *(undefined4 *)(param_1 + 0xd44);
                local_244 = *(undefined4 *)(&DAT_00001f6c + param_1);
                uVar9 = FUN_00084200();
                FUN_00b21c60(uVar9,param_1 + 0xce9,&local_418);
                *(byte *)(param_1 + 0x1f80) = *(byte *)(param_1 + 0x1f80) | 0x20;
              }
            }
            else if (iVar1 == 1) {
              lVar10 = FUN_00b0c560(*(undefined4 *)(param_1 + 0xcd0));
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
              local_180 = 0;
              uStack_178 = 0;
              uStack_170 = 0;
              uStack_168 = 0;
              local_1a0 = 0;
              uStack_198 = 0;
              uStack_190 = 0;
              uStack_188 = 0;
              local_1c0 = 0;
              uStack_1b8 = 0;
              uStack_1b0 = 0;
              uStack_1a8 = 0;
              local_1e0 = 0;
              uStack_1d8 = 0;
              uStack_1d0 = 0;
              uStack_1c8 = 0;
              local_200 = 0;
              uStack_1f8 = 0;
              uStack_1f0 = 0;
              uStack_1e8 = 0;
              local_220 = 0;
              uStack_218 = 0;
              uStack_210 = 0;
              uStack_208 = 0;
              local_240 = 0;
              uStack_238 = 0;
              uStack_230 = 0;
              uStack_228 = 0;
              local_80 = 0;
              if (((*(byte *)(lVar10 + 0x1b9) & 1) == 0) || ((*(byte *)(param_1 + 0x1f80) & 4) == 0)
                 ) goto LAB_00b2bbd1;
              FUN_00b2c490(lVar10,&local_240);
              uVar9 = FUN_00b10a70(param_1);
              FUN_0076e2b0(uVar12,uVar9);
              local_80 = CONCAT44(*(undefined4 *)(&DAT_00001f6c + param_1),
                                  *(undefined4 *)(param_1 + 0xd44));
              FUN_00b10490(param_1);
              uVar9 = FUN_00084200();
              FUN_00b21ad0(uVar9,param_1 + 0xce9,&local_240);
              *(byte *)(param_1 + 0x1f80) = *(byte *)(param_1 + 0x1f80) | 0x20;
            }
            if ((*(byte *)(param_1 + 0x1f80) & 0x20) != 0) {
              FUN_0076dfd0(*(undefined4 *)(&DAT_00001f6c + param_1),
                           *(undefined4 *)(FUN_00001f70 + param_1),uVar12,
                           *(undefined4 *)(param_1 + 0xcd0),*(undefined4 *)(param_1 + 0xd44),
                           (&DAT_00001db8)[param_1]);
            }
          }
        }
      }
    }
  }
LAB_00b2bc1b:
  if ((*(byte *)(param_1 + 0x1f80) & 0x20) == 0) goto LAB_00b2bd0f;
  lVar10 = FUN_00772ec0(iVar1);
  iVar5 = FUN_00b21430(iVar1);
  cVar3 = FUN_00b21070(iVar1);
  if ((cVar3 != '\0') || (iVar5 == 1)) goto LAB_00b2bd0f;
  if (iVar5 == 0) {
    if ((*(ushort *)(param_1 + 0x1f80) & 0x100) == 0) {
      if ((*(ushort *)(param_1 + 0x1f80) & 2) == 0) {
        FUN_00b21f70(iVar1);
        uVar4 = *(ushort *)(param_1 + 0x1f80) | 0x100;
      }
      else {
        FUN_00b22020();
        uVar4 = *(ushort *)(param_1 + 0x1f80);
        *(ushort *)(param_1 + 0x1f80) = uVar4 | 0x40;
        uVar4 = uVar4 | 0x140;
      }
    }
    else {
      if ((10 < *(uint *)(lVar10 + 0x8c48)) ||
         ((0x7f0U >> (*(uint *)(lVar10 + 0x8c48) & 0x1f) & 1) == 0)) {
        FUN_00b22190(iVar1);
        iVar5 = 0;
        goto LAB_00b2bd00;
      }
      cVar3 = FUN_00b742d0(lVar10);
      if ((cVar3 == '\0') ||
         (lVar10 = FUN_00b74340(lVar10),
         *(int *)(lVar10 + 0x5c + (long)*(int *)(lVar10 + 0x5d0c) * 0x168) != 10))
      goto LAB_00b2bd0f;
      uVar4 = *(ushort *)(param_1 + 0x1f80);
      if ((uVar4 & 2) == 0) {
        uVar4 = uVar4 | 0x80;
        *(ushort *)(param_1 + 0x1f80) = uVar4;
      }
      uVar4 = uVar4 & 0xfedf;
    }
    *(ushort *)(param_1 + 0x1f80) = uVar4;
  }
  else {
    FUN_00b220e0(iVar1);
LAB_00b2bd00:
    FUN_00b10880(param_1,param_1 + 0xcd8,iVar5);
    *(ushort *)(param_1 + 0x1f80) = *(ushort *)(param_1 + 0x1f80) & 0xfedf;
  }
LAB_00b2bd0f:
  if (((*(byte *)(param_1 + 0x1f80) & 0x40) != 0) && (cVar3 = FUN_00b224e0(iVar1), cVar3 == '\0')) {
    *(byte *)(param_1 + 0x1f80) = *(byte *)(param_1 + 0x1f80) & 0xbf;
  }
  if (*DAT_01a1f100 != local_60) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

