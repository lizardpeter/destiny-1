
undefined8 FUN_002aada0(long param_1,long param_2)

{
  undefined4 uVar1;
  char cVar2;
  int iVar3;
  long lVar4;
  undefined8 uVar5;
  ulong uVar6;
  undefined4 uVar7;
  char cVar8;
  undefined1 local_180 [8];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_000f2e30(local_180,*(undefined4 *)(param_1 + 0x41e0));
  uVar6 = *(ulong *)(param_2 + 0x48);
  *(ulong *)(param_1 + 0x4030) = uVar6;
  lVar4 = *(long *)(param_1 + 0x4028);
  if (lVar4 == 0) {
LAB_002aae2d:
    *(ulong *)(param_1 + 0x4038) = uVar6;
    lVar4 = FUN_000b0aa0((long)&DAT_01ad5000 +
                         (ulong)*(ushort *)(param_1 + 0x4020) * DAT_01ad5010 + DAT_01ad5000,uVar6);
    *(long *)(param_1 + 0x4028) = lVar4;
    if (lVar4 == 0) {
      cVar2 = FUN_000e4d70(0xd,4);
      uVar7 = 6;
      cVar8 = '\0';
      if (cVar2 != '\0') {
        if (DAT_0265b038 == '\0') {
          iVar3 = thunk_FUN_012aa7d6(&DAT_0265b038);
          if (iVar3 != 0) {
            DAT_0265b030 = FUN_000e4a10(s_networking_signon_client__Could_n_01624917);
            thunk_FUN_012aa7e6(&DAT_0265b038);
          }
        }
        cVar8 = '\0';
        FUN_01008290(local_178,s_networking_signon_client__Could_n_01624917,
                     *(undefined8 *)(param_1 + 0x4030));
        FUN_000e4aa0(DAT_0265b030,local_178);
      }
      goto LAB_002aafad;
    }
    uVar6 = *(ulong *)(param_1 + 0x4030);
  }
  else if (*(ulong *)(param_1 + 0x4038) < uVar6) {
    FUN_000b0bd0((long)&DAT_01ad5000 +
                 (ulong)*(ushort *)(param_1 + 0x4020) * DAT_01ad5010 + DAT_01ad5000,lVar4);
    *(undefined8 *)(param_1 + 0x4028) = 0;
    uVar6 = *(ulong *)(param_1 + 0x4030);
    goto LAB_002aae2d;
  }
  thunk_FUN_012aa7c6(lVar4,param_2 + 0x50,uVar6);
  *(undefined4 *)(param_1 + 0x4024) = 0;
  *(undefined8 *)(param_1 + 0x41c7) = 0;
  *(undefined8 *)(param_1 + 0x41bf) = 0;
  uVar5 = *(undefined8 *)(param_2 + 0x20);
  *(undefined8 *)(param_1 + 0x41c7) = *(undefined8 *)(param_2 + 0x28);
  *(undefined8 *)(param_1 + 0x41bf) = uVar5;
  uVar7 = 3;
  cVar8 = '\x01';
  *(undefined8 *)(param_1 + 0x41d7) = 0;
  *(undefined8 *)(param_1 + 0x41cf) = 0;
  uVar5 = *(undefined8 *)(param_2 + 0x38);
  *(undefined8 *)(param_1 + 0x41d7) = *(undefined8 *)(param_2 + 0x40);
  *(undefined8 *)(param_1 + 0x41cf) = uVar5;
  if (*(char *)(param_2 + 0x260) != '\0') {
    *(undefined4 *)(param_1 + 0x41e4) = *(undefined4 *)(param_2 + 0x264);
    *(undefined4 *)(param_1 + 0x41e8) = *(undefined4 *)(param_2 + 0x268);
    *(undefined4 *)(param_1 + 0x41ec) = *(undefined4 *)(param_2 + 0x26c);
  }
LAB_002aafad:
  FUN_000f2e70(local_180);
  if (*(int *)(param_2 + 600) != 0) {
    uVar1 = swap_bytes(*(int *)(param_2 + 600));
    *(undefined4 *)(param_1 + 0x41f0) = uVar1;
    *(undefined2 *)(param_1 + 0x41f4) = *(undefined2 *)(param_2 + 0x25c);
  }
  if (*(char *)(param_2 + 0x270) == '\0') {
    lVar4 = *(long *)(param_2 + 0x250);
  }
  else {
    lVar4 = FUN_000696a0();
    lVar4 = lVar4 + *(long *)(param_2 + 0x278);
  }
  *(long *)(param_1 + 0x4200) = lVar4;
  if (cVar8 == '\0') {
    *(undefined8 *)(param_1 + 0x4030) = 0;
    *(undefined4 *)(param_1 + 0x41f0) = 0;
    *(undefined2 *)(param_1 + 0x41f4) = 0;
    *(undefined8 *)(param_1 + 0x41f8) = 0;
  }
  *(undefined4 *)(param_1 + 0x4040) = uVar7;
  *(undefined1 *)(param_1 + 0x424d) = 0;
  cVar2 = FUN_000e4d70(0xd,2);
  if (cVar2 != '\0') {
    if (DAT_0295c080 == '\0') {
      iVar3 = thunk_FUN_012aa7d6(&DAT_0295c080);
      if (iVar3 != 0) {
        DAT_0295c078 = FUN_000e4a10(s_networking_signon_client__Signon_01624bdc);
        thunk_FUN_012aa7e6(&DAT_0295c080);
      }
    }
    FUN_01008290(local_178,s_networking_signon_client__Signon_01624bdc,
                 (&PTR_s__none_01911110)[*(uint *)(param_1 + 0x4040)]);
    FUN_000e4aa0(DAT_0295c078,local_178);
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),cVar8);
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

