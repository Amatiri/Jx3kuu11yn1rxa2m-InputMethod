#Include "dictionary+t.ahk"
Global 中英文:="中文"
Global 当前字词:=""
Shift::
{
	Global 中英文:=!中英文
	if(中英文)
	{
		TraySetIcon("chinese.ico")
		ToolTip()
	}
	Else
	{
		TraySetIcon("eng.ico")
		ToolTip()
	}
}
TraySetIcon("chinese.ico")

#HotIf 中英文
a::
b::
c::
d::
e::
f::
g::
h::
i::
j::
k::
l::
m::
n::
o::
p::
q::
r::
s::
t::
u::
v::
w::
x::
y::
z::
1::
2::
3::
4::
5::
6::
7::
8::
9::
0::

{
	CaretGetPos(&x, &y)
	Global 当前字词:=当前字词 . A_ThisHotkey
	if(当前字词 && %当前字词%)
	{
		ToolTip(当前字词 . "`n" . %当前字词%)
	}
	Else
	{
		ToolTip(当前字词)
	}
}
Space::
{
	Global 当前字词
	if(当前字词 && %当前字词%)
	{
		Send(%当前字词%)
	}
	当前字词:=""
	ToolTip()
}