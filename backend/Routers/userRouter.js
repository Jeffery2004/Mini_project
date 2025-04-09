const router=require('express').Router();
const User=require('../Models/userModel');
const bcrypt=require('bcrypt');
const jwt=require('jsonwebtoken');
const JWT_SECRET="secretcode";

router.post('/profile', async (req, res) => {
    const token = req.body.token;
    if (!token) {
      return res.status(401).json({ message: 'No token provided' });
    }  
    try {
      const decoded = jwt.verify(token, JWT_SECRET);
      const user = await User.findById(decoded.userId);
      return res.json({name:user.name,email:user.email,link:user.githublink});
    }catch(e){
        return res.status(400).send("error");
    }
});
router.post('/login',async(req,res)=>{
    const {email,password}=req.body;
    if(!email || !password){
        return res.json({message:"incomplete"});
    }
    try{
        const user=await User.findOne({email})
        if(!user){
            res.status(400).send("Not found");
        }
        const validPassword=await bcrypt.compare(password,user.password);
        if(!validPassword){
            res.status(400).send("Wrong password");
        }

        const token = jwt.sign({ userId: user._id, email: user.email },JWT_SECRET,{ expiresIn: '1h' });
        return res.status(200).json({
            message: "User logged in successfully",
            token: token
        });
    }catch(err){
        return res.status(400).send("User not found");
    }
})
router.post('/signup',async(req,res)=>{
    let {name,email,password,githublink}=req.body;
    const user=await User.findOne({email});
    if(!email || !password || !name || !githublink){
        return res.json({message:"incomplete"});
    }
    if(user){
        return res.json({message:"registered"});
    }
    try {
        password = await bcrypt.hash(password, 10);
        const newUser=await User.create({ name, email, password ,githublink})
        const token = jwt.sign({ userId: newUser._id, email: newUser.email }, JWT_SECRET, { expiresIn: '1h' });
        return res.json({
            message: "User created successfully",
            token :token
        });
    } catch (err) {
        console.error(err);
        return res.status(500).send("User not created");
    }
})

module.exports=router;  