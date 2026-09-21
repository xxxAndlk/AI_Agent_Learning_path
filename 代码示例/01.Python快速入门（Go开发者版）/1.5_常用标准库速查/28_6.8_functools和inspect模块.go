// Go的反射和函数工具
import (
    "reflect"
    "runtime"
)

// 获取类型信息
v := MyStruct{}
t := reflect.TypeOf(v)
fmt.Println(t.Name(), t.Kind())

// 获取函数名
f := exampleFunction
fmt.Println(runtime.FuncForPC(reflect.ValueOf(f).Pointer()).Name())

// 运行时调用
reflect.ValueOf(v).MethodByName("Method").Call(nil)
