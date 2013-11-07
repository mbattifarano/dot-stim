import video

video.Base.dfns=video.Base.dfns()

frame=video.Frame(0)

to_draw=[]
spots=[video.Sprite(im='circle-red',xypos=(0,0),size=0.25),
        video.Sprite(xypos=(3,4),size=0.25),
        video.Sprite(xypos=(-3,4),size=0.25),
        video.Sprite(xypos=(3,-4),size=0.25),
        video.Sprite(xypos=(-3,-4),size=0.25),
        video.Sprite(xypos=(0,5),size=0.25),
        video.Sprite(xypos=(5,0),size=0.25)]

patch=video.DotField()

to_draw.append(patch)
to_draw.extend(spots)

frame.add_object(to_draw)
frame.render()
frame.write()


