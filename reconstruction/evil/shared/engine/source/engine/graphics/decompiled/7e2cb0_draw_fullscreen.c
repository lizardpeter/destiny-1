
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_007e2cb0(undefined8 param_1,undefined8 param_2,long *param_3,int param_4,int param_5)

{
  undefined4 *puVar1;
  long lVar2;
  undefined1 auVar3 [16];
  undefined1 auVar4 [16];
  long lVar5;
  undefined1 (*pauVar6) [16];
  undefined8 uVar7;
  undefined4 uVar8;
  undefined4 *puVar9;
  long lVar10;
  undefined8 in_XMM0_Qb;
  undefined8 in_XMM1_Qb;
  undefined1 auVar11 [16];
  
  lVar5 = *param_3;
  puVar1 = *(undefined4 **)(lVar5 + 0x132f0);
  if ((undefined4 *)param_3[0x3a5] != puVar1) {
    if (puVar1 == (undefined4 *)0x0) {
      lVar5 = param_3[10];
      puVar9 = (undefined4 *)0x0;
      uVar8 = 0;
      uVar7 = 0;
    }
    else {
      lVar5 = param_3[10];
      uVar7 = *(undefined8 *)(puVar1 + 2);
      uVar8 = *puVar1;
      puVar9 = puVar1 + 5;
    }
    FUN_00f8b790(lVar5 + 0xc0,puVar9,uVar8,uVar7);
    param_3[0x3a5] = (long)puVar1;
    lVar5 = *param_3;
  }
  lVar5 = *(long *)(lVar5 + 0x132f8);
  if (param_3[0x3a6] != lVar5) {
    if (lVar5 == 0) {
      lVar2 = param_3[10];
      lVar10 = 0;
    }
    else {
      lVar2 = param_3[10];
      lVar10 = lVar5;
    }
    FUN_00f8b8c0(lVar2 + 0xc0,lVar10);
    param_3[0x3a6] = lVar5;
  }
  pauVar6 = (undefined1 (*) [16])FUN_00f7feb0(param_3[10],0x10,4);
  if (pauVar6 != (undefined1 (*) [16])0x0) {
    auVar11._0_4_ = _DAT_0165feb8 / (float)param_5;
    auVar11._4_12_ = SUB6012((undefined1  [60])0x0,0);
    auVar11 = vinsertps_avx(ZEXT416((uint)(_DAT_0165feb8 / (float)param_4)),auVar11,0x10);
    auVar3._8_8_ = in_XMM0_Qb;
    auVar3._0_8_ = param_1;
    auVar11 = vinsertps_avx(auVar11,auVar3,0x20);
    auVar4._8_8_ = in_XMM1_Qb;
    auVar4._0_8_ = param_2;
    auVar11 = vinsertps_avx(auVar11,auVar4,0x30);
    *pauVar6 = auVar11;
    FUN_00f7d180(*param_3 + 0x13300,pauVar6,0xa0);
    FUN_00f7d010(*param_3 + 0x13300,0x10);
    FUN_00f8b500(param_3[10] + 0xc0,2,0,1,*param_3 + 0x13300);
  }
  FUN_007de4a0(param_3,1);
  if ((int)param_3[0x4b8] != 1) {
    FUN_00f81a90((long)param_3 + 0x25d4,DAT_015d23a4,DAT_015d23a4);
    FUN_00f7e100((long)param_3 + 0x25d4,DAT_015d23a8);
    FUN_00f81c50(param_3 + 0x4ba,DAT_015d23ac ^ 1,DAT_015d23ac ^ 1);
    FUN_00f80790(param_3[10],*(undefined4 *)((long)param_3 + 0x25d4));
    FUN_00f80640(param_3[10],(int)param_3[0x4ba]);
    *(undefined4 *)(param_3 + 0x4b8) = 1;
  }
  if (*(char *)((long)param_3 + 0x26) != '\0') {
    FUN_00f7f1e0(param_3[10],0x11);
    lVar5 = param_3[10];
    FUN_00f8df60(lVar5 + 0xc0,lVar5,lVar5 + 0x80);
    FUN_00f7f260(lVar5,3);
    FUN_00f8e880(lVar5 + 0xc0,lVar5,lVar5 + 0x80);
    return;
  }
  return;
}

