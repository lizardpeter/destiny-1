
void FUN_007de370(float param_1,float param_2,long param_3,uint param_4,uint param_5,uint param_6,
                 uint param_7)

{
  long *plVar1;
  float local_38;
  float local_34;
  float local_30;
  float local_2c;
  float local_28;
  float local_24;
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  local_2c = (float)param_6 * DAT_0165fe58;
  local_24 = DAT_0165fe5c / (param_2 - param_1);
  local_28 = (float)param_7 * DAT_0165fe60;
  local_30 = param_1 / (param_2 - param_1);
  local_34 = (float)param_5 + (float)param_7 * DAT_0165fe58;
  local_38 = (float)param_4 + local_2c;
  *(uint *)(param_3 + 0x2578) = param_4;
  *(uint *)(param_3 + 0x257c) = param_5;
  *(uint *)(param_3 + 0x2580) = param_6;
  *(uint *)(&DAT_00002584 + param_3) = param_7;
  *(float *)(&DAT_00002588 + param_3) = param_1;
  *(float *)(&DAT_0000258c + param_3) = param_2;
  FUN_00f80340(*(undefined8 *)(param_3 + 0x50),0,&local_2c,&local_38);
  if (*plVar1 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

