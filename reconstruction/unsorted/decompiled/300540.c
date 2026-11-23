
void FUN_00300540(void)

{
  undefined8 *puVar1;
  ushort uVar2;
  undefined8 *puVar3;
  undefined4 uVar4;
  
  uVar4 = 0xffffffff;
  if (DAT_01914588 != (undefined4 *)0x0) {
    uVar4 = *DAT_01914588;
  }
  FUN_0023e010(&DAT_02689540,s_9simulation_queue_simulation_que_01629e23 + 1,0x70,4,uVar4,10,3,0x19,
               thunk_FUN_001681a0);
  puVar1 = DAT_02689540;
  puVar3 = (undefined8 *)0x0;
  if (DAT_02689540 != (undefined8 *)0x0) {
    DAT_02689540[0xd] = 0;
    puVar1[0xc] = 0;
    puVar1[0xb] = 0;
    puVar1[10] = 0;
    puVar1[9] = 0;
    puVar1[8] = 0;
    puVar1[7] = 0;
    puVar1[6] = 0;
    puVar1[5] = 0;
    puVar1[4] = 0;
    puVar1[3] = 0;
    puVar1[2] = 0;
    puVar1[1] = 0;
    *puVar1 = 0;
    *(undefined1 *)puVar1 = 0;
    *(undefined1 *)(puVar1 + 5) = 0;
    *(undefined2 *)(puVar1 + 10) = 0xffff;
    puVar3 = DAT_02689540;
  }
  uVar2 = FUN_000b0c70(1,0x76c00,0x19,s_simulation_queue_heap_01629e4e);
  *(ushort *)(puVar3 + 10) = uVar2;
  puVar3[0xb] = (long)&DAT_01ad5000 + (ulong)uVar2 * DAT_01ad5010 + DAT_01ad5000;
  *(undefined1 *)((long)puVar3 + 0x6c) = 0;
  *(undefined4 *)(puVar3 + 0xd) = 0;
  puVar3[0xc] = 0;
  puVar1 = DAT_02689540;
  FUN_002ff570(DAT_02689540 + 5,0xba000);
  FUN_002ff570(puVar1,0x3e000);
  return;
}

