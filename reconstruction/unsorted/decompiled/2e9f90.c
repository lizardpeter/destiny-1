
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_002e9f90(undefined2 *param_1)

{
  long *plVar1;
  long *in_FS_OFFSET;
  undefined1 local_68;
  undefined1 local_67 [40];
  undefined1 local_3f;
  undefined1 local_3e;
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  local_68 = 0x7b;
  FUN_000652e0(local_67,0x29,s__03x__08x__04x__04x__02x_02x__02_01628fdf,*param_1,
               *(undefined4 *)(param_1 + 1),param_1[3],param_1[4],*(undefined1 *)(param_1 + 5),
               *(undefined1 *)((long)param_1 + 0xb),*(undefined1 *)(param_1 + 6),
               *(undefined1 *)((long)param_1 + 0xd),*(undefined1 *)(param_1 + 7),
               *(undefined1 *)((long)param_1 + 0xf),*(undefined1 *)(param_1 + 8),
               *(undefined1 *)((long)param_1 + 0x11));
  local_3f = 0x7d;
  local_3e = 0;
  FUN_010310d0(*in_FS_OFFSET + _DAT_01a1f380,&DAT_0160ed63,&local_68);
  if (*plVar1 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

