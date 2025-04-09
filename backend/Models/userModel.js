const mongoose=require('mongoose');
const UserSchema=mongoose.Schema({
    name:{
        type:String,
        required:true
    },
    email:{
        type:String,
        required:true
    },
    password:{
        type:String,
        require:true
    },
    githublink:{
        type:String,
        required:true
    }
},{timestamps:true})
const Users=mongoose.model('Users',UserSchema);
module.exports=Users;