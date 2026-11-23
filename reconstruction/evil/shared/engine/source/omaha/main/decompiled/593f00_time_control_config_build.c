
/* WARNING: Removing unreachable block (ram,0x005942e8) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00593f00(undefined4 *param_1)

{
  float fVar1;
  undefined4 *puVar2;
  uint *puVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined8 uVar6;
  ulong uVar7;
  long lVar8;
  undefined8 *puVar9;
  long lVar10;
  long lVar11;
  undefined4 uVar12;
  undefined8 in_stack_ffffffffffffffc8;
  
  uVar4 = (uint)((ulong)in_stack_ffffffffffffffc8 >> 0x20);
  DAT_026bcdd0 = FUN_000f97b0(FUN_00594330,s_time_control_wakeup_job_0163ea80,0);
  uVar5 = 0xffffffff;
  FUN_00070530(&DAT_026bcd50,s_Fiber_Frame_Time_Info_0163ea98,DAT_01940630,0x48,8,0xffffffff,3,0x2d0
               ,(ulong)uVar4 << 0x20,0x1d,0);
  if (DAT_01941a58 != (undefined4 *)0x0) {
    uVar5 = *DAT_01941a58;
  }
  FUN_0023e010(&DAT_026bcd08,s_time_control_config_globals_0163eaae,0x48,4,uVar5,0,0,0xd,
               thunk_FUN_001681a0);
  puVar2 = DAT_026bcd08;
  *DAT_026bcd08 = *param_1;
  fVar1 = DAT_0163ea4c;
  lVar11 = (long)(DAT_0163ea4c * (float)param_1[1]);
  *(long *)(puVar2 + 6) = lVar11;
  lVar8 = (long)(fVar1 * (float)param_1[2]);
  *(long *)(puVar2 + 8) = lVar8;
  lVar10 = (long)(fVar1 * (float)param_1[3]);
  *(long *)(puVar2 + 10) = lVar10;
  *(long *)(puVar2 + 0xc) = (long)(fVar1 * (float)param_1[4]);
  *(long *)(puVar2 + 2) = (long)(fVar1 * (float)param_1[5]);
  *(long *)(puVar2 + 4) = (long)(fVar1 * (float)param_1[6]);
  puVar2[0xe] = param_1[7];
  *(long *)(puVar2 + 0x10) = (long)(fVar1 * (float)param_1[8]);
  if (lVar11 < 0) {
    *(long *)(puVar2 + 6) = lVar11 + lVar10;
  }
  if (lVar8 < 0) {
    *(long *)(puVar2 + 8) = lVar10 + lVar8;
  }
  uVar12 = 0xffffffff;
  uVar5 = 0xffffffff;
  if (DAT_01941a48 != (undefined4 *)0x0) {
    uVar5 = *DAT_01941a48;
  }
  FUN_0023e010(&DAT_026bcd18,s_time_control_globals_0163eaca,0x80,4,uVar5,0,3,0xd,thunk_FUN_001681a0
              );
  puVar9 = DAT_026bcd18;
  *DAT_026bcd18 = 0;
  uVar6 = thunk_FUN_012aac96();
  puVar9[1] = uVar6;
  lVar8 = thunk_FUN_012aac86();
  *(float *)(puVar9 + 5) = (float)lVar8 / DAT_0163ea50;
  puVar9[4] = 0;
  puVar9[3] = 0;
  puVar9[2] = 0;
  *(undefined1 *)((long)puVar9 + 0x7c) = 1;
  *(undefined4 *)(puVar9 + 6) = 0;
  *(undefined2 *)((long)puVar9 + 0x34) = 0xffff;
  *(undefined2 *)((long)puVar9 + 0x36) = 0;
  *(undefined4 *)(puVar9 + 7) = 0;
  *(undefined2 *)((long)puVar9 + 0x3c) = 0xffff;
  *(undefined2 *)((long)puVar9 + 0x3e) = 0;
  *(undefined4 *)(puVar9 + 8) = 0;
  *(undefined2 *)((long)puVar9 + 0x44) = 0xffff;
  *(undefined2 *)((long)puVar9 + 0x46) = 0;
  *(undefined4 *)(puVar9 + 9) = 0;
  *(undefined2 *)((long)puVar9 + 0x4c) = 0xffff;
  *(undefined2 *)((long)puVar9 + 0x4e) = 0;
  *(undefined4 *)(puVar9 + 10) = 0;
  *(undefined2 *)((long)puVar9 + 0x54) = 0xffff;
  *(undefined2 *)((long)puVar9 + 0x56) = 0;
  *(undefined4 *)(puVar9 + 0xb) = 0;
  *(undefined4 *)((long)puVar9 + 0x5c) = 0xffff;
  puVar9[0xe] = 0xffffffffffffffff;
  puVar9[0xd] = 0xffffffffffffffff;
  puVar9[0xc] = 0xffffffffffffffff;
  *(undefined4 *)(puVar9 + 0xf) = 0;
  if (DAT_01941a38 != (undefined4 *)0x0) {
    uVar12 = *DAT_01941a38;
  }
  FUN_0023e010(&DAT_026bcd10,s_time_control_game_state_globals_0163eadf,0x10,4,uVar12,0,1,0xd,
               thunk_FUN_001681a0);
  puVar3 = DAT_026bcd10;
  DAT_026bcd10[(long)(int)DAT_026bcd10[3] + 1] = 0xffffffff;
  puVar3[((long)(int)puVar3[3] ^ 1U) + 1] = 0xffffffff;
  uVar4 = FUN_0006e750(&DAT_026bcd50);
  *puVar3 = uVar4;
  lVar11 = (ulong)(((uint)((int)uVar4 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar4 >> 0xd) * 0x40;
  lVar8 = *DAT_01a238a0;
  lVar10 = *(long *)(lVar8 + 0x10 + lVar11);
  uVar7 = (ulong)((uVar4 & 0x1fff) * *(int *)(lVar8 + 0x30 + lVar11));
  puVar9 = (undefined8 *)
           ((lVar10 + uVar7) -
           ((long)*(int *)(lVar8 + 0x34 + lVar11) & *(ulong *)(lVar10 + 8 + uVar7)));
  puVar9[8] = 0;
  puVar9[7] = 0;
  puVar9[6] = 0;
  puVar9[5] = 0;
  puVar9[4] = 0;
  puVar9[3] = 0;
  puVar9[2] = 0;
  puVar9[1] = 0;
  *puVar9 = 0;
  _DAT_026bcd40 = 0;
  _DAT_026bcd38 = 0;
  DAT_026bcd28 = 0;
  DAT_026bcd20 = 0;
  LOCK();
  _DAT_026bcd30 = 0x100000000;
  UNLOCK();
  uVar5 = thunk_FUN_000f6d70(&PTR_s_S4_Timecontrol_01941a20);
  _DAT_026bcd40 = CONCAT44(uVar5,DAT_026bcd40);
  DAT_01b074f0 = FUN_0058bf90;
  FUN_000c72a0(1);
  return;
}

