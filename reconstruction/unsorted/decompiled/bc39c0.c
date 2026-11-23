
undefined8 FUN_00bc39c0(undefined8 param_1,long param_2)

{
  byte bVar1;
  undefined4 uVar2;
  uint *puVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  char cVar6;
  uint uVar7;
  undefined8 in_RAX;
  undefined4 uVar8;
  uint uVar9;
  uint uVar10;
  bool bVar11;
  
  uVar8 = (undefined4)((ulong)in_RAX >> 0x20);
  bVar1 = *(byte *)(param_2 + 0x38);
  puVar3 = *(uint **)(param_2 + 8);
  uVar4 = *(undefined8 *)(param_2 + 0x28);
  uVar2 = *(undefined4 *)PTR_DAT_0191a858;
  uVar5 = *(undefined8 *)(param_2 + 0x30);
  cVar6 = FUN_00073430(uVar5);
  if (cVar6 != '\0') {
    FUN_002c84c0(uVar2,uVar5,0,uVar4,uVar4,puVar3,CONCAT44(uVar8,(uint)bVar1));
    uVar7 = puVar3[2];
    uVar9 = (int)(uVar7 << 0x12) >> 0x12;
    if (((uVar9 & 0xfffffffe) == 0xfffffffe) ||
       ((uVar10 = *puVar3, uVar9 != 0 && (bVar11 = uVar10 != 0, uVar10 = 0, bVar11)))) {
      if ((uVar7 & 0x3fff) != 0x3ffe) {
        thunk_FUN_002c72d0(puVar3,1);
      }
      **(uint **)puVar3 = **(uint **)puVar3 | 1;
      uVar7 = puVar3[2];
    }
    else {
      *puVar3 = uVar10 | 1;
      uVar7 = uVar7 & 0xffffc000;
      puVar3[2] = uVar7;
    }
    if ((int)(uVar7 << 4) >> 0x12 < 1) {
      puVar3[2] = uVar7 & 0xf0003fff | 0x4000;
    }
  }
  return 1;
}

