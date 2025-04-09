const express=require('express');
const mongoose=require("mongoose");
const mongourl="mongodb://localhost:27017/AI_CODE_REVIEW";
const app=express();
const cors=require('cors');
app.use(cors());
app.use(express.json());
const userRouter=require('./Routers/userRouter')

app.use('/user',userRouter);

mongoose.connect(mongourl)
.then(()=>{
    app.listen(3000,()=>{
        console.log("connected")
    })
}).catch((err)=>{
    console.log(err);
})