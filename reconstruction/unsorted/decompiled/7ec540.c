
void FUN_007ec540(undefined4 *param_1)

{
  long lVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  long lVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  ulong uVar8;
  undefined8 *puVar9;
  undefined8 in_R9;
  
  lVar1 = *DAT_01a1f100;
  FUN_00836ea0();
  iVar4 = FUN_008114e0();
  if (iVar4 != 0) {
    FUN_00075cd0(&DAT_026e4040);
    lVar5 = FUN_007eab70();
    if (lVar5 != 0) {
      FUN_00803d70(lVar5);
      *(undefined1 *)(lVar5 + 0x191e8) = 0;
      *(undefined1 *)(lVar5 + 0x191e9) = DAT_02707ed4;
      FUN_008173a0(&DAT_026f22c0);
      *(undefined2 *)(&LAB_000187d4 + lVar5) = *(undefined2 *)(param_1 + 1);
      *(undefined4 *)(lVar5 + 0x187d0) = *param_1;
      *(undefined4 *)(lVar5 + 0x192ec) = 0;
      *(undefined4 *)(lVar5 + 0x192f0) = 0;
      *(undefined1 *)(lVar5 + 0x1b330) = 0;
      uVar6 = FUN_0023d130(1);
      uVar7 = FUN_000fb400(4,DAT_026e42ec,DAT_025d12ad,lVar5,7,in_R9,DAT_025d11c0,DAT_025d11c8,
                           DAT_025d11c0,DAT_025d11c8,DAT_025d11c0,DAT_025d11c8);
      *(undefined8 *)(lVar5 + 0x186c8) = uVar7;
      *(undefined4 *)(lVar5 + 0x186d0) = 0;
      *(undefined4 *)(lVar5 + 0x186d4) = 0xffff;
      FUN_000fb670(uVar7,uVar6);
      uVar6 = FUN_0023d130(3);
      FUN_000fb670(uVar6,*(undefined8 *)(lVar5 + 0x186c8));
      uVar7 = FUN_000fb400(5,DAT_026e42e0,DAT_025d12ad,lVar5,7,in_R9,DAT_025d11c0,DAT_025d11c8,
                           DAT_025d11c0,DAT_025d11c8,DAT_025d11c0,DAT_025d11c8);
      *(undefined8 *)(lVar5 + 0x186c0) = uVar7;
      uVar7 = FUN_0023d130(6);
      *(undefined8 *)(lVar5 + 0x186b0) = uVar7;
      *(undefined8 *)(lVar5 + 0x186b8) = uVar7;
      FUN_000fb670(*(undefined8 *)(lVar5 + 0x186c0),uVar7);
      uVar8 = FUN_0023d130(7);
      FUN_000fb670(uVar8,*(undefined8 *)(lVar5 + 0x186c0));
      if ((uVar8 & 0xffff00000000) != 0xffff00000000) {
        uVar7 = FUN_0023d130(5);
        *(undefined8 *)(lVar5 + 100000) = uVar7;
        uVar7 = FUN_0023d130(2);
        *(undefined8 *)(lVar5 + 0x18698) = uVar7;
        FUN_00803e20(lVar5);
        cVar2 = FUN_007ec9b0(lVar5);
        cVar3 = '\x01';
        if (cVar2 != '\0') {
          cVar3 = FUN_00811540(lVar5,&DAT_026e3da0,&DAT_026e4040);
        }
        FUN_000fb5c0(*(undefined8 *)(lVar5 + 0x186c0));
        uVar7 = FUN_000fb400(4,DAT_026e42e8,DAT_025d12ad,lVar5,7,in_R9,DAT_025d11c0,DAT_025d11c8,
                             DAT_025d11c0,DAT_025d11c8,DAT_025d11c0,DAT_025d11c8);
        *(undefined8 *)(lVar5 + 0x186a8) = uVar7;
        FUN_000fb670(uVar6,uVar7);
        FUN_000fb670(*(undefined8 *)(lVar5 + 0x186a8),*(undefined8 *)(lVar5 + 0x18698));
        FUN_000fb670(*(undefined8 *)(lVar5 + 100000),*(undefined8 *)(lVar5 + 0x186a8));
        FUN_000fb5c0(*(undefined8 *)(lVar5 + 0x186a8));
        cVar2 = FUN_00805340(0xd);
        if (cVar2 == '\0') {
          *(undefined4 *)(lVar5 + 0x187a0) = 0;
          *(undefined2 *)(lVar5 + 0x187a4) = 0xffff;
          *(undefined2 *)(lVar5 + 0x187a6) = 0;
          *(undefined4 *)(lVar5 + 0x187a8) = 0;
          *(undefined4 *)(lVar5 + 0x187ac) = 0xffff;
        }
        else {
          uVar6 = FUN_0087d6e0(lVar5);
          *(undefined8 *)(lVar5 + 0x187a0) = uVar6;
          uVar6 = FUN_0087d850(*(undefined8 *)(lVar5 + 0x1fc50));
          *(undefined8 *)(lVar5 + 0x187a8) = uVar6;
        }
        FUN_000fb5c0(*(undefined8 *)(lVar5 + 0x186c8));
        if (cVar3 == '\0') {
          FUN_00075d90(&DAT_026e3da0);
          puVar9 = (undefined8 *)FUN_007eab70();
          if (puVar9 != (undefined8 *)0x0) {
            puVar9[2] = 0;
            puVar9[1] = 0;
            *puVar9 = 0;
            FUN_007eabd0(puVar9);
          }
          FUN_007eab40(0);
        }
      }
    }
  }
  if (*DAT_01a1f100 == lVar1) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

