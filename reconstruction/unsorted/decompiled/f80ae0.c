
void FUN_00f80ae0(long param_1,int param_2,ulong param_3)

{
  long lVar1;
  char cVar2;
  uint uVar3;
  undefined8 *puVar4;
  uint *puVar5;
  ulong uVar6;
  uint uVar7;
  
  uVar3 = 8;
  if (param_2 == 0) {
    uVar3 = 0x16;
  }
  if (((uint)((ulong)(*(long *)(param_1 + 8) - *(long *)(param_1 + 0x10)) >> 2) < uVar3) &&
     (cVar2 = (**(code **)(param_1 + 0x18))(param_1,uVar3,*(undefined8 *)(param_1 + 0x20)),
     cVar2 == '\0')) {
    return;
  }
  if (param_2 != 0) {
    puVar5 = *(uint **)(param_1 + 0x10);
    goto LAB_00f80bff;
  }
  puVar4 = *(undefined8 **)(param_1 + 0x10);
  uVar3 = (uint)(param_3 >> 0x20);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar4) >> 2) < 7) {
    cVar2 = (**(code **)(param_1 + 0x18))(param_1,7,*(undefined8 *)(param_1 + 0x20));
    puVar4 = *(undefined8 **)(param_1 + 0x10);
    if (cVar2 != '\0') goto LAB_00f80b5e;
  }
  else {
LAB_00f80b5e:
    *puVar4 = 0xc4004000c0055000;
    *(undefined4 *)(puVar4 + 1) = 0;
    *(undefined4 *)((long)puVar4 + 0xc) = 0;
    *(uint *)(puVar4 + 2) = (uint)param_3;
    *(uint *)((long)puVar4 + 0x14) = uVar3;
    *(undefined4 *)(puVar4 + 3) = 0x80;
    puVar4 = (undefined8 *)(*(long *)(param_1 + 0x10) + 0x1c);
    *(undefined8 **)(param_1 + 0x10) = puVar4;
  }
  *(undefined4 *)puVar4 = 0xc0053c00;
  uVar7 = 0xffff;
  if (0xffff < param_3) {
    uVar7 = 0xfffffffc;
  }
  *(uint *)((long)puVar4 + 4) = (uint)(0xffff < param_3) << 4 | 0x105;
  *(uint *)(puVar4 + 1) = (uint)param_3 & uVar7;
  *(uint *)((long)puVar4 + 0xc) = uVar3 & 0xffff;
  *(undefined4 *)(puVar4 + 2) = 0;
  *(undefined4 *)((long)puVar4 + 0x14) = 0xffffffff;
  *(undefined4 *)(puVar4 + 3) = 10;
  puVar5 = (uint *)(*(long *)(param_1 + 0x10) + 0x1c);
  *(uint **)(param_1 + 0x10) = puVar5;
LAB_00f80bff:
  uVar3 = *(uint *)(param_1 + 0x28) & 2 | 0xc0024600;
  *puVar5 = uVar3;
  puVar5[1] = 0x138;
  puVar5[2] = 0x7fc00;
  puVar5[3] = 0;
  uVar6 = param_3 + 8;
  if (param_2 != 1) {
    uVar6 = param_3;
  }
  lVar1 = *(long *)(param_1 + 0x10);
  *(long *)(param_1 + 0x10) = lVar1 + 0x10;
  *(uint *)(lVar1 + 0x10) = uVar3;
  *(undefined4 *)(lVar1 + 0x14) = 0x139;
  *(uint *)(lVar1 + 0x18) = (uint)uVar6 & 0xfffffff8;
  *(uint *)(lVar1 + 0x1c) = (uint)(uVar6 >> 0x20) & 0xff;
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0x10;
  return;
}

