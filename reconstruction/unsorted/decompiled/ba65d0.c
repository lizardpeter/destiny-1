
void FUN_00ba65d0(undefined8 *param_1)

{
  uint *puVar1;
  char cVar2;
  uint uVar3;
  ulong uVar4;
  long *plVar5;
  undefined1 local_140 [64];
  undefined1 local_100 [90];
  undefined1 local_a6;
  undefined8 local_70;
  undefined8 local_68;
  undefined8 local_60;
  undefined8 local_58;
  undefined8 local_50;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  puVar1 = (uint *)(param_1 + 2);
  uVar4 = 0;
  do {
    if (((*puVar1 >> ((uint)uVar4 & 0x1f) & 1) != 0) &&
       (*(char *)(param_1 + uVar4 * 0x1d + 4) == '\0')) {
      uVar3 = 0;
      plVar5 = (long *)((long)param_1 + 0x12ec);
      do {
        if (((*(uint *)((long)param_1 + 0x12dc) >> (uVar3 & 0x1f) & 1) != 0) &&
           (*plVar5 == param_1[uVar4 * 0x1d + 5])) goto LAB_00ba66f0;
        plVar5 = plVar5 + 1;
        uVar3 = uVar3 + 1;
      } while ((int)uVar3 < 0x14);
      thunk_FUN_012aa986(local_100,0,0x90);
      local_a6 = 0xff;
      local_50 = 0;
      local_58 = 0;
      local_60 = 0;
      local_68 = 0;
      local_70 = 0xffffffff;
      FUN_00ba90d0(local_140,puVar1,uVar4 & 0xffffffff,param_1 + uVar4 * 0x1d + 3,0);
      cVar2 = FUN_00bb6b20(*param_1,uVar4 & 0xffffffff,0);
      if (cVar2 != '\0') {
        FUN_00bb6aa0(*param_1,uVar4 & 0xffffffff);
      }
    }
LAB_00ba66f0:
    uVar4 = uVar4 + 1;
    if ((int)uVar4 == 0x14) {
      *(undefined4 *)(param_1 + 0x247) = *(undefined4 *)((long)param_1 + 0x12dc);
      thunk_FUN_012aa7c6((long)param_1 + 0x123c,(long *)((long)param_1 + 0x12ec),0xa0);
      FUN_00b9b720(puVar1);
      *(undefined4 *)((long)param_1 + 0xc) = 0xffffffff;
      if (*DAT_01a1f100 == local_38) {
        return;
      }
      thunk_FUN_012aa7f6();
      return;
    }
  } while( true );
}

