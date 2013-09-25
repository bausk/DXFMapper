-- Lua script.
p=tetview:new()
p:load_mesh("C:/Users/cadm/Documents/GitHub/PyDfxCoder/PyDfxCoder_VS10/test.face")
rnd=glvCreate(0, 0, 500, 500, "TetView")
p:plot(rnd)
glvWait()
